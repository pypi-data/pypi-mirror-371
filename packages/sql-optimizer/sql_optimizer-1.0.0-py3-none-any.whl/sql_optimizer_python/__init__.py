"""
SQL Query Optimizer Python Package

A Python wrapper for the Java-based SQL Query Optimizer using Apache Calcite.
"""

from .optimizer import SqlOptimizer, OptimizationRule, OptimizationEngine
from .exceptions import SqlOptimizerError, JavaRuntimeError, OptimizationError, MetadataError, RulesError

__version__ = "1.0.0"
__author__ = "SQL Optimizer Team"

__all__ = [
    "SqlOptimizer",
    "OptimizationRule",
    "OptimizationEngine",
    "SqlOptimizerError",
    "JavaRuntimeError",
    "OptimizationError",
    "MetadataError",
    "RulesError"
]
