"""Custom exceptions for JSON Compare Pro."""

from typing import Any, Dict, Optional


class JSONCompareError(Exception):
    """Base exception for JSON comparison errors."""
    
    def __init__(self, message: str, details: Optional[Dict[str, Any]] = None):
        super().__init__(message)
        self.message = message
        self.details = details or {}


class ValidationError(JSONCompareError):
    """Raised when validation fails during JSON comparison."""
    
    def __init__(self, message: str, key: Optional[str] = None, value1: Any = None, value2: Any = None):
        details = {"key": key, "value1": value1, "value2": value2}
        super().__init__(message, details)
        self.key = key
        self.value1 = value1
        self.value2 = value2


class SchemaValidationError(JSONCompareError):
    """Raised when JSON schema validation fails."""
    
    def __init__(self, message: str, schema_errors: Optional[list] = None):
        details = {"schema_errors": schema_errors}
        super().__init__(message, details)
        self.schema_errors = schema_errors or []


class JSONPathError(JSONCompareError):
    """Raised when JSONPath operations fail."""
    
    def __init__(self, message: str, jsonpath: Optional[str] = None):
        details = {"jsonpath": jsonpath}
        super().__init__(message, details)
        self.jsonpath = jsonpath


class ConfigurationError(JSONCompareError):
    """Raised when there's an error in the comparison configuration."""
    pass


class UnsupportedTypeError(JSONCompareError):
    """Raised when an unsupported data type is encountered."""
    
    def __init__(self, message: str, data_type: Optional[str] = None):
        details = {"data_type": data_type}
        super().__init__(message, details)
        self.data_type = data_type 