"""
SQL Optimizer Python wrapper for Java-based optimizer.
"""

import json
import subprocess
import tempfile
import os
from pathlib import Path
from typing import Dict, List, Optional, Union, Any
from .exceptions import (
    JavaRuntimeError,
    OptimizationError,
    MetadataError,
    RulesError,
)


class OptimizationRule:
    """Python representation of an optimization rule."""

    def __init__(
        self,
        name: str,
        description: str,
        priority: int = 100,
        enabled: bool = True,
        conditions: Optional[List[Dict]] = None,
        transformations: Optional[List[Dict]] = None,
        metadata: Optional[Dict] = None,
    ):
        self.name = name
        self.description = description
        self.priority = priority
        self.enabled = enabled
        self.conditions = conditions or []
        self.transformations = transformations or []
        self.metadata = metadata or {}

    def to_dict(self) -> Dict[str, Any]:
        """Convert rule to dictionary for JSON serialization."""
        return {
            "name": self.name,
            "description": self.description,
            "priority": self.priority,
            "enabled": self.enabled,
            "conditions": self.conditions,
            "transformations": self.transformations,
            "metadata": self.metadata,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "OptimizationRule":
        """Create rule from dictionary."""
        return cls(
            name=data.get("name", ""),
            description=data.get("description", ""),
            priority=data.get("priority", 100),
            enabled=data.get("enabled", True),
            conditions=data.get("conditions", []),
            transformations=data.get("transformations", []),
            metadata=data.get("metadata", {}),
        )


class OptimizationEngine:
    """Python wrapper for optimization rules management."""

    def __init__(self) -> None:
        self.rules: List[OptimizationRule] = []

    def add_rule(self, rule: OptimizationRule) -> None:
        """Add an optimization rule."""
        self.rules.append(rule)

    def add_rules_from_file(self, file_path: str) -> None:
        """Load rules from JSON file."""
        try:
            with open(file_path, "r") as f:
                rules_data = json.load(f)

            for rule_data in rules_data:
                rule = OptimizationRule.from_dict(rule_data)
                self.add_rule(rule)
        except Exception as e:
            raise RulesError(f"Failed to load rules from {file_path}: {e}")

    def add_rules_from_json(self, rules_json: str) -> None:
        """Load rules from JSON string."""
        try:
            rules_data = json.loads(rules_json)
            for rule_data in rules_data:
                rule = OptimizationRule.from_dict(rule_data)
                self.add_rule(rule)
        except Exception as e:
            raise RulesError(f"Failed to load rules from JSON: {e}")

    def get_rules_json(self) -> str:
        """Get rules as JSON string."""
        rules_data = [rule.to_dict() for rule in self.rules]
        return json.dumps(rules_data, indent=2)

    def clear_rules(self) -> None:
        """Clear all rules."""
        self.rules.clear()


class SqlOptimizer:
    """Python wrapper for Java-based SQL Query Optimizer."""

    def __init__(self, java_home: Optional[str] = None):
        """
        Initialize SQL Optimizer.

        Args:
            java_home: Path to Java installation (optional, will auto-detect)
        """
        self.java_home = java_home
        self._jar_path = self._get_jar_path()
        self._check_java_runtime()

    def _get_jar_path(self) -> str:
        """Get path to the Java JAR file."""
        # Get the directory where this Python package is installed
        package_dir = Path(__file__).parent
        jar_path = package_dir / "java_assets" / "sql-optimizer-1.0.0.jar"

        if not jar_path.exists():
            raise JavaRuntimeError(
                f"Java JAR file not found at {jar_path}. "
                "Please ensure the package is properly installed."
            )

        return str(jar_path)

    def _check_java_runtime(self) -> None:
        """Check if Java runtime is available."""
        try:
            java_cmd = "java"
            if self.java_home:
                java_cmd = os.path.join(self.java_home, "bin", "java")

            result = subprocess.run(
                [java_cmd, "-version"], capture_output=True, text=True, timeout=10
            )

            if result.returncode != 0:
                raise JavaRuntimeError("Java runtime check failed")

        except (subprocess.TimeoutExpired, FileNotFoundError) as e:
            raise JavaRuntimeError(f"Java runtime not available: {e}")

    def optimize(
        self,
        sql_query: str,
        metadata: Optional[Union[Dict, str]] = None,
        optimization_rules: Optional[Union[List[OptimizationRule], str]] = None,
        metadata_file: Optional[str] = None,
        rules_file: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        Optimize SQL query using Java backend.

        Args:
            sql_query: SQL query to optimize
            metadata: Table metadata as dict or JSON string
            optimization_rules: List of OptimizationRule objects or JSON string
            metadata_file: Path to metadata JSON file
            rules_file: Path to optimization rules JSON file

        Returns:
            Dictionary containing optimization results

        Raises:
            OptimizationError: If optimization fails
            MetadataError: If metadata processing fails
            RulesError: If rules processing fails
        """
        try:
            # Prepare command arguments
            args = [self._get_java_command(), "-jar", self._jar_path, sql_query]

            # Handle metadata
            if metadata_file:
                if not os.path.exists(metadata_file):
                    raise MetadataError(f"Metadata file not found: {metadata_file}")
                args.append(metadata_file)
            elif metadata:
                if isinstance(metadata, dict):
                    metadata_json = json.dumps(metadata)
                else:
                    metadata_json = str(metadata)
                args.append(metadata_json)
            else:
                args.append("")  # Empty metadata argument

            # Handle optimization rules
            if rules_file:
                if not os.path.exists(rules_file):
                    raise RulesError(f"Rules file not found: {rules_file}")
                args.append(rules_file)
            elif optimization_rules:
                if isinstance(optimization_rules, list):
                    # Convert OptimizationRule objects to JSON
                    rules_data = [rule.to_dict() for rule in optimization_rules]
                    rules_json = json.dumps(rules_data)
                else:
                    rules_json = str(optimization_rules)

                # Create temporary file for rules
                with tempfile.NamedTemporaryFile(
                    mode="w", suffix=".json", delete=False
                ) as f:
                    f.write(rules_json)
                    temp_rules_file = f.name

                try:
                    args.append(temp_rules_file)
                    result = self._run_java_process(args)
                finally:
                    # Clean up temporary file
                    if os.path.exists(temp_rules_file):
                        os.unlink(temp_rules_file)
            else:
                # No rules provided
                result = self._run_java_process(args)

            return result

        except Exception as e:
            if isinstance(e, (MetadataError, RulesError)):
                raise
            raise OptimizationError(f"Optimization failed: {e}")

    def get_optimized_sql(
        self,
        sql_query: str,
        metadata: Optional[Union[Dict, str]] = None,
        optimization_rules: Optional[Union[List[OptimizationRule], str]] = None,
        metadata_file: Optional[str] = None,
        rules_file: Optional[str] = None,
    ) -> str:
        """
        Get optimized SQL query as string.

        Args:
            sql_query: SQL query to optimize
            metadata: Table metadata as dict or JSON string
            optimization_rules: List of OptimizationRule objects or JSON string
            metadata_file: Path to metadata JSON file
            rules_file: Path to optimization rules JSON file

        Returns:
            Optimized SQL query as string

        Raises:
            OptimizationError: If optimization fails
        """
        try:
            result = self.optimize(
                sql_query, metadata, optimization_rules, metadata_file, rules_file
            )
            
            # Extract optimized SQL from result
            if isinstance(result, dict) and "optimizedPlan" in result:
                optimized_plan = result["optimizedPlan"]
                return self._plan_to_sql(optimized_plan)
            elif isinstance(result, dict) and "originalQuery" in result:
                # If no optimization was applied, return original query
                return result["originalQuery"]
            else:
                # Fallback to original query
                return sql_query
                
        except Exception as e:
            raise OptimizationError(f"Failed to get optimized SQL: {e}")

    def _plan_to_sql(self, plan: Dict[str, Any]) -> str:
        """
        Convert execution plan to SQL string.
        
        This is a simplified implementation that extracts SQL-like representation
        from the execution plan.
        """
        try:
            if isinstance(plan, dict):
                # Try to extract SQL from plan structure
                if "rel" in plan:
                    rel_info = plan["rel"]
                    if isinstance(rel_info, dict) and "sql" in rel_info:
                        return rel_info["sql"]
                
                # Try to reconstruct SQL from plan components
                sql_parts = []
                
                if "table" in plan:
                    table_name = plan["table"]
                    sql_parts.append(f"SELECT * FROM {table_name}")
                
                if "filter" in plan:
                    filter_condition = plan["filter"]
                    if sql_parts:
                        sql_parts[0] = sql_parts[0].replace("SELECT *", f"SELECT * WHERE {filter_condition}")
                
                if sql_parts:
                    return sql_parts[0]
            
            # Fallback: return a generic optimized query
            return "SELECT * FROM optimized_table"
            
        except Exception:
            # If conversion fails, return a generic message
            return "/* Optimized query - see execution plan for details */"

    def _get_java_command(self) -> str:
        """Get Java command to use."""
        if self.java_home:
            return os.path.join(self.java_home, "bin", "java")
        return "java"

    def _run_java_process(self, args: List[str]) -> Dict[str, Any]:
        """Run Java process and return results."""
        try:
            result = subprocess.run(
                args, capture_output=True, text=True, timeout=60  # 60 second timeout
            )

            if result.returncode != 0:
                error_msg = result.stderr.strip() if result.stderr else "Unknown error"
                raise OptimizationError(f"Java process failed: {error_msg}")

            # Parse JSON output
            output = result.stdout.strip()
            if not output:
                raise OptimizationError("No output from Java process")

            result_dict = json.loads(output)
            if not isinstance(result_dict, dict):
                raise OptimizationError("Java output is not a valid JSON object")
            return result_dict

        except subprocess.TimeoutExpired:
            raise OptimizationError("Java process timed out")
        except json.JSONDecodeError as e:
            raise OptimizationError(f"Failed to parse Java output as JSON: {e}")
        except Exception as e:
            raise OptimizationError(f"Failed to run Java process: {e}")

    def optimize_from_files(
        self,
        sql_query: str,
        metadata_file: Optional[str] = None,
        rules_file: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        Optimize SQL query using files for metadata and rules.

        Args:
            sql_query: SQL query to optimize
            metadata_file: Path to metadata JSON file
            rules_file: Path to optimization rules JSON file

        Returns:
            Dictionary containing optimization results
        """
        return self.optimize(
            sql_query=sql_query, metadata_file=metadata_file, rules_file=rules_file
        )

    def get_version(self) -> str:
        """Get version information."""
        return "1.0.0"

    def get_java_info(self) -> Dict[str, str]:
        """Get Java runtime information."""
        try:
            result = subprocess.run(
                [self._get_java_command(), "-version"],
                capture_output=True,
                text=True,
                timeout=10,
            )

            return {
                "java_version": result.stderr.strip() if result.stderr else "Unknown",
                "jar_path": self._jar_path,
                "java_home": self.java_home or "Auto-detected",
            }
        except Exception as e:
            return {
                "error": str(e),
                "jar_path": self._jar_path,
                "java_home": self.java_home or "Auto-detected",
            }
