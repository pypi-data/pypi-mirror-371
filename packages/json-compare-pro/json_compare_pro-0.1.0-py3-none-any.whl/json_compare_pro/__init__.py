"""
JSON Compare Pro - Advanced JSON comparison library with flexible validation rules.

A comprehensive library for comparing JSON objects with support for:
- Flexible key ignoring and value validation
- Custom validation rules (regex, patterns, etc.)
- Schema validation
- JSONPath support
- Tolerance checks for numeric values
- Detailed diff reporting
- CLI interface
"""

__version__ = "0.1.0"
__author__ = "Harshit Goel"
__email__ = "harshitgoel96@gmail.com"

from .core import (
    JSONCompareConfig,
    JSONCompareResult,
    compare_jsons,
    compare_jsons_with_config,
)
from .validators import (
    CustomValidator,
    NumericToleranceValidator,
    RegexValidator,
    StringPatternValidator,
    EMAIL_VALIDATOR,
    URL_VALIDATOR,
    UUID_VALIDATOR,
    DATE_VALIDATOR,
    TIMESTAMP_VALIDATOR,
)
from .schema import JSONSchemaValidator, create_user_schema
from .jsonpath import JSONPathExtractor
from .diff import JSONDiffReporter, DiffFormatter
from .exceptions import (
    JSONCompareError,
    ValidationError,
    SchemaValidationError,
    JSONPathError,
)

__all__ = [
    # Core functionality
    "compare_jsons",
    "compare_jsons_with_config",
    "JSONCompareConfig",
    "JSONCompareResult",
    
    # Validators
    "CustomValidator",
    "NumericToleranceValidator", 
    "RegexValidator",
    "StringPatternValidator",
    "EMAIL_VALIDATOR",
    "URL_VALIDATOR",
    "UUID_VALIDATOR",
    "DATE_VALIDATOR",
    "TIMESTAMP_VALIDATOR",
    
    # Schema validation
    "JSONSchemaValidator",
    "create_user_schema",
    
    # JSONPath support
    "JSONPathExtractor",
    
    # Diff reporting
    "JSONDiffReporter",
    "DiffFormatter",
    
    # Exceptions
    "JSONCompareError",
    "ValidationError",
    "SchemaValidationError",
    "JSONPathError",
] 