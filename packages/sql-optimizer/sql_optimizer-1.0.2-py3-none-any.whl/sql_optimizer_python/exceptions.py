"""
Custom exceptions for SQL Optimizer Python package.
"""


class SqlOptimizerError(Exception):
    """Base exception for SQL Optimizer errors."""

    pass


class JavaRuntimeError(SqlOptimizerError):
    """Raised when Java runtime is not available or fails."""

    pass


class OptimizationError(SqlOptimizerError):
    """Raised when optimization process fails."""

    pass


class MetadataError(SqlOptimizerError):
    """Raised when metadata processing fails."""

    pass


class RulesError(SqlOptimizerError):
    """Raised when optimization rules processing fails."""

    pass

