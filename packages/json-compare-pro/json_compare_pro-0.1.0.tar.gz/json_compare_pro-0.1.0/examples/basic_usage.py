#!/usr/bin/env python3
"""
Basic usage examples for JSON Compare Pro.

This script demonstrates the core functionality of the library.
"""

import json
from json_compare_pro import (
    compare_jsons,
    compare_jsons_with_config,
    JSONCompareConfig,
    JSONSchemaValidator,
    JSONPathExtractor,
    JSONDiffReporter,
    DiffFormatter,
    create_user_schema,
    EMAIL_VALIDATOR,
    URL_VALIDATOR,
    TIMESTAMP_VALIDATOR,
)


def basic_comparison_example():
    """Demonstrate basic JSON comparison."""
    print("=== Basic Comparison Example ===")
    
    # Sample JSON objects
    json1 = {
        "name": "John Doe",
        "age": 30,
        "email": "john@example.com",
        "active": True,
        "scores": [85, 92, 78]
    }
    
    json2 = {
        "name": "John Doe",
        "age": 30,
        "email": "john@example.com",
        "active": True,
        "scores": [85, 92, 78]
    }
    
    # Simple comparison
    result = compare_jsons(json1, json2)
    print(f"Basic comparison result: {result}")
    
    # Compare with differences
    json2["age"] = 31
    result = compare_jsons(json1, json2)
    print(f"Comparison with difference: {result}")


def advanced_configuration_example():
    """Demonstrate advanced configuration options."""
    print("\n=== Advanced Configuration Example ===")
    
    json1 = {
        "id": "12345",
        "name": "John Doe",
        "email": "JOHN@EXAMPLE.COM",
        "timestamp": "2023-01-01T10:00:00Z",
        "scores": [85, 92, 78]
    }
    
    json2 = {
        "id": "67890",
        "name": "John Doe",
        "email": "john@example.com",
        "timestamp": "2023-01-01T10:00:01Z",
        "scores": [78, 85, 92]
    }
    
    # Advanced configuration
    config = JSONCompareConfig(
        keys_to_ignore=["id"],  # Ignore ID field
        case_sensitive=False,   # Case insensitive comparison
        ignore_order=True,      # Ignore array order
        numeric_tolerance=2.0,  # Allow 2-second tolerance for timestamps
        custom_validators={
            "email": EMAIL_VALIDATOR,
            "timestamp": TIMESTAMP_VALIDATOR
        }
    )
    
    result = compare_jsons_with_config(json1, json2, config)
    print(f"Advanced comparison result: {result.is_equal}")
    print(f"Differences found: {len(result.differences)}")
    
    if result.differences:
        print("Differences:")
        for diff in result.differences:
            print(f"  - {diff['message']}")


def custom_validation_example():
    """Demonstrate custom validation rules."""
    print("\n=== Custom Validation Example ===")
    
    json1 = {
        "email": "john@example.com",
        "phone": "123-456-7890",
        "website": "https://example.com",
        "score": 85
    }
    
    json2 = {
        "email": "jane@example.com",
        "phone": "987-654-3210",
        "website": "https://test.com",
        "score": 92
    }
    
    # Custom validation rules
    custom_validations = {
        "email": {"type": "endswith", "expected": "@example.com"},
        "phone": {"type": "regex", "expected": r"\d{3}-\d{3}-\d{4}"},
        "website": {"type": "startswith", "expected": "https://"},
        "score": {"type": "range", "min": 0, "max": 100}
    }
    
    result = compare_jsons(json1, json2, custom_validations=custom_validations)
    print(f"Custom validation result: {result}")


def schema_validation_example():
    """Demonstrate schema validation."""
    print("\n=== Schema Validation Example ===")
    
    # Create a user schema
    schema = create_user_schema()
    print("Generated user schema:")
    print(json.dumps(schema, indent=2))
    
    # Valid user data
    valid_user = {
        "id": "12345",
        "name": "John Doe",
        "email": "john@example.com",
        "age": 30,
        "active": True
    }
    
    # Invalid user data (missing required fields)
    invalid_user = {
        "name": "John Doe",
        "age": 30
        # Missing required 'id' and 'email' fields
    }
    
    # Validate data
    validator = JSONSchemaValidator(schema)
    
    valid_result = validator.validate(valid_user)
    print(f"Valid user validation: {valid_result.is_valid}")
    
    invalid_result = validator.validate(invalid_user)
    print(f"Invalid user validation: {invalid_result.is_valid}")
    
    if not invalid_result.is_valid:
        print("Validation errors:")
        for error in invalid_result.errors:
            print(f"  - {error['message']} at {' -> '.join(map(str, error['path']))}")


def jsonpath_example():
    """Demonstrate JSONPath functionality."""
    print("\n=== JSONPath Example ===")
    
    # Sample data with nested structure
    data = {
        "users": [
            {
                "id": 1,
                "name": "John Doe",
                "email": "john@example.com",
                "profile": {
                    "age": 30,
                    "city": "New York"
                }
            },
            {
                "id": 2,
                "name": "Jane Smith",
                "email": "jane@example.com",
                "profile": {
                    "age": 25,
                    "city": "Los Angeles"
                }
            }
        ],
        "metadata": {
            "total": 2,
            "version": "1.0"
        }
    }
    
    # Extract values using JSONPath
    extractor = JSONPathExtractor()
    
    # Get all user names
    names_result = extractor.find(data, "$.users[*].name")
    print(f"User names: {names_result.values}")
    
    # Get all email addresses
    emails_result = extractor.find(data, "$.users[*].email")
    print(f"Email addresses: {emails_result.values}")
    
    # Get users older than 25
    older_users = extractor.filter_by_path(
        data, 
        "$.users[*]", 
        lambda user, path: user.get("profile", {}).get("age", 0) > 25
    )
    print(f"Users older than 25: {[user['name'] for user in older_users.values]}")


def diff_reporting_example():
    """Demonstrate detailed diff reporting."""
    print("\n=== Diff Reporting Example ===")
    
    json1 = {
        "name": "John Doe",
        "age": 30,
        "email": "john@example.com",
        "scores": [85, 92, 78],
        "metadata": {
            "created": "2023-01-01",
            "version": "1.0"
        }
    }
    
    json2 = {
        "name": "John Doe",
        "age": 31,
        "email": "john.doe@example.com",
        "scores": [85, 78, 92],
        "metadata": {
            "created": "2023-01-01",
            "version": "2.0"
        },
        "new_field": "added"
    }
    
    # Generate detailed diff
    reporter = JSONDiffReporter()
    diff_report = reporter.generate_diff(json1, json2)
    
    print(f"Diff report summary:")
    print(f"  Total differences: {diff_report.summary['total_differences']}")
    print(f"  Difference types: {diff_report.summary['type_counts']}")
    
    # Format as text
    text_diff = DiffFormatter.to_text(diff_report)
    print("\nText diff:")
    print(text_diff)
    
    # Format as markdown
    markdown_diff = DiffFormatter.to_markdown(diff_report)
    print("\nMarkdown diff (first 500 chars):")
    print(markdown_diff[:500] + "...")


def main():
    """Run all examples."""
    print("JSON Compare Pro - Basic Usage Examples")
    print("=" * 50)
    
    try:
        basic_comparison_example()
        advanced_configuration_example()
        custom_validation_example()
        schema_validation_example()
        jsonpath_example()
        diff_reporting_example()
        
        print("\n" + "=" * 50)
        print("All examples completed successfully!")
        
    except Exception as e:
        print(f"\nError running examples: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main() 