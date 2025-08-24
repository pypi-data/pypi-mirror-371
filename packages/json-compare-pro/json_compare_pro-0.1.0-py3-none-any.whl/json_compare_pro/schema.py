"""JSON Schema validation functionality."""

from typing import Any, Dict, List, Optional, Union
from dataclasses import dataclass

from .exceptions import SchemaValidationError


@dataclass
class SchemaValidationResult:
    """Result of schema validation."""
    
    is_valid: bool
    errors: List[Dict[str, Any]] = None
    warnings: List[str] = None
    
    def __post_init__(self):
        if self.errors is None:
            self.errors = []
        if self.warnings is None:
            self.warnings = []
    
    def __bool__(self) -> bool:
        """Return True if validation was successful."""
        return self.is_valid


class JSONSchemaValidator:
    """JSON Schema validator using jsonschema library."""
    
    def __init__(self, schema: Optional[Dict[str, Any]] = None):
        """
        Initialize the schema validator.
        
        Args:
            schema: JSON schema to use for validation
        """
        self.schema = schema
        self._validator = None
        
        if schema:
            self._load_validator()
    
    def _load_validator(self) -> None:
        """Load the jsonschema validator."""
        try:
            from jsonschema import Draft202012Validator, ValidationError as JSONSchemaValidationError
            self._validator = Draft202012Validator(self.schema)
        except ImportError:
            raise ImportError(
                "jsonschema library is required for schema validation. "
                "Install it with: pip install jsonschema"
            )
        except Exception as e:
            raise SchemaValidationError(f"Failed to load schema validator: {str(e)}")
    
    def validate(self, data: Dict[str, Any]) -> SchemaValidationResult:
        """
        Validate data against the schema.
        
        Args:
            data: Data to validate
            
        Returns:
            SchemaValidationResult with validation details
        """
        if not self._validator:
            raise SchemaValidationError("No schema loaded. Set a schema first.")
        
        result = SchemaValidationResult(is_valid=True)
        
        try:
            errors = list(self._validator.iter_errors(data))
            
            if errors:
                result.is_valid = False
                for error in errors:
                    result.errors.append({
                        "path": list(error.path),
                        "message": error.message,
                        "validator": error.validator,
                        "validator_value": error.validator_value,
                        "instance": error.instance,
                        "schema_path": list(error.schema_path),
                    })
            
        except Exception as e:
            result.is_valid = False
            result.errors.append({
                "path": [],
                "message": f"Validation failed with error: {str(e)}",
                "validator": None,
                "validator_value": None,
                "instance": data,
                "schema_path": [],
            })
        
        return result
    
    def set_schema(self, schema: Dict[str, Any]) -> None:
        """
        Set a new schema for validation.
        
        Args:
            schema: New JSON schema
        """
        self.schema = schema
        self._load_validator()
    
    def validate_both(self, data1: Dict[str, Any], data2: Dict[str, Any]) -> Dict[str, SchemaValidationResult]:
        """
        Validate both data objects against the schema.
        
        Args:
            data1: First data object
            data2: Second data object
            
        Returns:
            Dictionary with validation results for both objects
        """
        return {
            "data1": self.validate(data1),
            "data2": self.validate(data2)
        }


class SchemaBuilder:
    """Builder for creating JSON schemas programmatically."""
    
    def __init__(self):
        self.schema = {"type": "object", "properties": {}, "required": []}
    
    def add_property(self, name: str, property_schema: Dict[str, Any], required: bool = False) -> 'SchemaBuilder':
        """
        Add a property to the schema.
        
        Args:
            name: Property name
            property_schema: Property schema definition
            required: Whether the property is required
            
        Returns:
            Self for method chaining
        """
        self.schema["properties"][name] = property_schema
        
        if required and name not in self.schema["required"]:
            self.schema["required"].append(name)
        
        return self
    
    def add_string_property(self, name: str, required: bool = False, **kwargs) -> 'SchemaBuilder':
        """Add a string property."""
        property_schema = {"type": "string", **kwargs}
        return self.add_property(name, property_schema, required)
    
    def add_number_property(self, name: str, required: bool = False, **kwargs) -> 'SchemaBuilder':
        """Add a number property."""
        property_schema = {"type": "number", **kwargs}
        return self.add_property(name, property_schema, required)
    
    def add_integer_property(self, name: str, required: bool = False, **kwargs) -> 'SchemaBuilder':
        """Add an integer property."""
        property_schema = {"type": "integer", **kwargs}
        return self.add_property(name, property_schema, required)
    
    def add_boolean_property(self, name: str, required: bool = False) -> 'SchemaBuilder':
        """Add a boolean property."""
        property_schema = {"type": "boolean"}
        return self.add_property(name, property_schema, required)
    
    def add_array_property(self, name: str, items_schema: Dict[str, Any], required: bool = False, **kwargs) -> 'SchemaBuilder':
        """Add an array property."""
        property_schema = {"type": "array", "items": items_schema, **kwargs}
        return self.add_property(name, property_schema, required)
    
    def add_object_property(self, name: str, properties_schema: Dict[str, Any], required: bool = False, **kwargs) -> 'SchemaBuilder':
        """Add an object property."""
        property_schema = {"type": "object", "properties": properties_schema, **kwargs}
        return self.add_property(name, property_schema, required)
    
    def add_email_property(self, name: str, required: bool = False) -> 'SchemaBuilder':
        """Add an email property."""
        property_schema = {
            "type": "string",
            "format": "email"
        }
        return self.add_property(name, property_schema, required)
    
    def add_uri_property(self, name: str, required: bool = False) -> 'SchemaBuilder':
        """Add a URI property."""
        property_schema = {
            "type": "string",
            "format": "uri"
        }
        return self.add_property(name, property_schema, required)
    
    def add_uuid_property(self, name: str, required: bool = False) -> 'SchemaBuilder':
        """Add a UUID property."""
        property_schema = {
            "type": "string",
            "format": "uuid"
        }
        return self.add_property(name, property_schema, required)
    
    def add_date_property(self, name: str, required: bool = False) -> 'SchemaBuilder':
        """Add a date property."""
        property_schema = {
            "type": "string",
            "format": "date"
        }
        return self.add_property(name, property_schema, required)
    
    def add_datetime_property(self, name: str, required: bool = False) -> 'SchemaBuilder':
        """Add a datetime property."""
        property_schema = {
            "type": "string",
            "format": "date-time"
        }
        return self.add_property(name, property_schema, required)
    
    def set_additional_properties(self, allow: bool) -> 'SchemaBuilder':
        """Set whether additional properties are allowed."""
        self.schema["additionalProperties"] = allow
        return self
    
    def set_pattern_properties(self, patterns: Dict[str, Dict[str, Any]]) -> 'SchemaBuilder':
        """Set pattern properties."""
        self.schema["patternProperties"] = patterns
        return self
    
    def build(self) -> Dict[str, Any]:
        """Build and return the final schema."""
        return self.schema.copy()


# Pre-built schemas
def create_user_schema() -> Dict[str, Any]:
    """Create a schema for user data."""
    builder = SchemaBuilder()
    builder.add_string_property("id", required=True)
    builder.add_string_property("name", required=True)
    builder.add_email_property("email", required=True)
    builder.add_string_property("phone", required=False)
    builder.add_integer_property("age", required=False, minimum=0, maximum=150)
    builder.add_boolean_property("active", required=False)
    return builder.build()


def create_product_schema() -> Dict[str, Any]:
    """Create a schema for product data."""
    builder = SchemaBuilder()
    builder.add_string_property("id", required=True)
    builder.add_string_property("name", required=True)
    builder.add_string_property("description", required=False)
    builder.add_number_property("price", required=True, minimum=0)
    builder.add_integer_property("stock", required=True, minimum=0)
    builder.add_array_property("categories", {"type": "string"}, required=False)
    builder.add_boolean_property("available", required=False)
    return builder.build()


def create_api_response_schema() -> Dict[str, Any]:
    """Create a schema for API response data."""
    builder = SchemaBuilder()
    builder.add_integer_property("status_code", required=True)
    builder.add_string_property("message", required=False)
    builder.add_object_property("data", {}, required=False)
    builder.add_array_property("errors", {"type": "string"}, required=False)
    return builder.build() 