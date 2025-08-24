#!/usr/bin/env python3
"""
Command-line interface for SQL Optimizer Python package.
"""

import argparse
import json
import sys

from .optimizer import SqlOptimizer, OptimizationEngine
from .exceptions import SqlOptimizerError


def main() -> int:
    """Main CLI entry point."""
    parser = argparse.ArgumentParser(
        description="SQL Query Optimizer - Python wrapper for Java-based optimizer",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Basic optimization
  sql-optimizer "SELECT * FROM employees"

  # With metadata
  sql-optimizer "SELECT * FROM custom_table" --metadata '{"custom_table":{"columns":{"id":{"type":"INTEGER"}}}}'

  # With metadata file
  sql-optimizer "SELECT * FROM custom_table" --metadata-file examples/custom_table_metadata.json

  # With optimization rules
  sql-optimizer "SELECT * FROM employees" --rules-file examples/basic_optimization_rules.json

  # With both metadata and rules
  sql-optimizer "SELECT * FROM custom_table" --metadata-file metadata.json --rules-file rules.json

  # Check Java runtime
  sql-optimizer --check-java
        """,
    )

    parser.add_argument("sql_query", nargs="?", help="SQL query to optimize")

    parser.add_argument("--metadata", help="Table metadata as JSON string")

    parser.add_argument("--metadata-file", help="Path to metadata JSON file")

    parser.add_argument("--rules", help="Optimization rules as JSON string")

    parser.add_argument("--rules-file", help="Path to optimization rules JSON file")

    parser.add_argument(
        "--java-home", help="Path to Java installation (optional, will auto-detect)"
    )

    parser.add_argument(
        "--check-java", action="store_true", help="Check Java runtime and exit"
    )

    parser.add_argument("--version", action="store_true", help="Show version and exit")

    parser.add_argument("--output", help="Output file for results (default: stdout)")

    parser.add_argument(
        "--pretty", action="store_true", help="Pretty print JSON output"
    )

    args = parser.parse_args()

    try:
        # Handle version flag
        if args.version:
            print("SQL Optimizer Python Package v1.0.0")
            return 0

        # Handle Java check flag
        if args.check_java:
            optimizer = SqlOptimizer(java_home=args.java_home)
            java_info = optimizer.get_java_info()
            print("Java Runtime Information:")
            print(json.dumps(java_info, indent=2))
            return 0

        # Check if SQL query is provided
        if not args.sql_query:
            parser.error(
                "SQL query is required (unless using --check-java or --version)"
            )

        # Initialize optimizer
        optimizer = SqlOptimizer(java_home=args.java_home)

        # Perform optimization
        result = optimizer.optimize(
            sql_query=args.sql_query,
            metadata=args.metadata,
            metadata_file=args.metadata_file,
            rules_file=args.rules_file,
        )

        # Handle rules as JSON string
        if args.rules:
            # Create temporary rules engine
            rules_engine = OptimizationEngine()
            rules_engine.add_rules_from_json(args.rules)

            # Perform optimization with rules
            result = optimizer.optimize(
                sql_query=args.sql_query,
                metadata=args.metadata,
                metadata_file=args.metadata_file,
                optimization_rules=rules_engine.rules,
            )

        # Format output
        if args.pretty:
            output_json = json.dumps(result, indent=2)
        else:
            output_json = json.dumps(result)

        # Write output
        if args.output:
            with open(args.output, "w") as f:
                f.write(output_json)
            print(f"Results written to {args.output}")
        else:
            print(output_json)

        return 0

    except SqlOptimizerError as e:
        print(f"Error: {e}", file=sys.stderr)
        return 1
    except KeyboardInterrupt:
        print("\nOperation cancelled by user", file=sys.stderr)
        return 1
    except Exception as e:
        print(f"Unexpected error: {e}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())
