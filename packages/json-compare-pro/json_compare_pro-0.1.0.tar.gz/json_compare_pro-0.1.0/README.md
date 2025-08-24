# JSON Compare Pro 🚀

[![PyPI version](https://badge.fury.io/py/json-compare-pro.svg)](https://badge.fury.io/py/json-compare-pro)
[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)
[![Tests](https://github.com/harshitgoel09/json-compare-pro/workflows/Tests/badge.svg)](https://github.com/harshitgoel09/json-compare-pro/actions)

**Advanced JSON comparison library with flexible validation rules, schema support, and comprehensive testing capabilities.**

JSON Compare Pro is a powerful, production-ready Python library designed for comparing JSON objects with advanced features like custom validation rules, schema validation, JSONPath support, tolerance checks, and detailed diff reporting. Perfect for API testing, data validation, and automated testing workflows.

## ✨ Features

### 🔍 **Advanced Comparison**
- **Flexible key ignoring** - Exclude specific keys from comparison
- **Key existence validation** - Check for key presence without comparing values
- **Custom validation rules** - Regex, patterns, ranges, and more
- **Numeric tolerance** - Handle floating-point precision issues
- **Case sensitivity options** - Configurable string comparison
- **Whitespace handling** - Ignore or preserve whitespace in strings
- **Array order control** - Compare arrays with or without order consideration

### 🛡️ **Schema Validation**
- **JSON Schema support** - Validate against JSON Schema specifications
- **Schema builder** - Programmatically create schemas
- **Pre-built schemas** - Common patterns for users, products, API responses
- **Detailed validation reports** - Comprehensive error reporting

### 🗺️ **JSONPath Support**
- **Advanced querying** - Extract and compare specific JSON paths
- **Path filtering** - Focus comparison on specific data subsets
- **Query builder** - Fluent API for building JSONPath expressions
- **Common patterns** - Pre-built queries for typical use cases

### 📊 **Detailed Diff Reporting**
- **Multiple output formats** - JSON, text, markdown, HTML, rich terminal
- **Categorized differences** - Added, removed, changed, type changes
- **Path-based reporting** - Exact location of differences
- **Summary statistics** - Quick overview of comparison results

### 🎯 **Production Ready**
- **Comprehensive testing** - 100% test coverage with edge cases
- **Type hints** - Full type annotation support
- **Error handling** - Robust exception handling with detailed messages
- **Performance optimized** - Efficient algorithms for large JSON objects
- **CLI interface** - Command-line tool for quick comparisons

## 🚀 Quick Start

### Installation

```bash
pip install json-compare-pro
```

### Basic Usage

```python
from json_compare_pro import compare_jsons

# Simple comparison
json1 = {"name": "John", "age": 30}
json2 = {"name": "John", "age": 30}

result = compare_jsons(json1, json2)
print(result)  # True
```

### Advanced Configuration

```python
from json_compare_pro import compare_jsons_with_config, JSONCompareConfig

# Advanced comparison with configuration
config = JSONCompareConfig(
    keys_to_ignore=["id", "timestamp"],
    check_keys_only=["status"],
    case_sensitive=False,
    ignore_order=True,
    numeric_tolerance=0.1
)

result = compare_jsons_with_config(json1, json2, config)
print(f"Equal: {result.is_equal}")
print(f"Differences: {len(result.differences)}")
print(f"Execution time: {result.execution_time:.4f}s")
```

### Custom Validation

```python
# Custom validation rules
custom_validations = {
    "email": {"type": "endswith", "expected": "@example.com"},
    "phone": {"type": "regex", "expected": r"\d{3}-\d{3}-\d{4}"},
    "score": {"type": "range", "min": 0, "max": 100}
}

result = compare_jsons(json1, json2, custom_validations=custom_validations)
```

### Schema Validation

```python
from json_compare_pro import JSONSchemaValidator, create_user_schema

# Create and use schema
schema = create_user_schema()
validator = JSONSchemaValidator(schema)

validation_result = validator.validate(json_data)
if validation_result.is_valid:
    print("✅ Data is valid!")
else:
    print(f"❌ Validation failed: {len(validation_result.errors)} errors")
```

### JSONPath Extraction

```python
from json_compare_pro import JSONPathExtractor

# Extract values using JSONPath
extractor = JSONPathExtractor()
result = extractor.find(json_data, "$.users[*].email")

print(f"Found {result.count} email addresses:")
for value, path in zip(result.values, result.paths):
    print(f"  {path}: {value}")
```

### Detailed Diff Report

```python
from json_compare_pro import JSONDiffReporter, DiffFormatter

# Generate detailed diff
reporter = JSONDiffReporter()
diff_report = reporter.generate_diff(json1, json2)

# Format as markdown
markdown_diff = DiffFormatter.to_markdown(diff_report)
print(markdown_diff)
```

## 🖥️ Command Line Interface

### Basic Comparison

```bash
# Compare two JSON files
json-compare file1.json file2.json

# With options
json-compare file1.json file2.json \
  --ignore-keys id timestamp \
  --check-keys-only status \
  --case-sensitive false \
  --output-format markdown \
  --output-file diff_report.md
```

### Generate Diff Report

```bash
# Generate detailed diff
json-compare diff file1.json file2.json \
  --output-format html \
  --output-file diff_report.html
```

### Extract with JSONPath

```bash
# Extract values using JSONPath
json-compare extract data.json "$.users[*].email" \
  --output-format json
```

### Schema Validation

```bash
# Validate against schema
json-compare validate data.json schema.json

# Generate schema
json-compare generate-schema --type user --output-file user_schema.json
```

## 📚 Advanced Examples

### API Testing Workflow

```python
import requests
from json_compare_pro import compare_jsons_with_config, JSONCompareConfig

# Test API response
def test_api_response():
    # Expected response structure
    expected = {
        "status": "success",
        "data": {
            "users": [
                {"id": "1", "name": "John", "email": "john@example.com"}
            ]
        }
    }
    
    # Actual API response
    response = requests.get("https://api.example.com/users")
    actual = response.json()
    
    # Compare with configuration
    config = JSONCompareConfig(
        keys_to_ignore=["data.users[0].id"],  # Ignore dynamic ID
        custom_validations={
            "data.users[*].email": {"type": "endswith", "expected": "@example.com"}
        },
        ignore_order=True  # Array order doesn't matter
    )
    
    result = compare_jsons_with_config(expected, actual, config)
    
    if result.is_equal:
        print("✅ API response matches expected structure")
    else:
        print("❌ API response differs:")
        for diff in result.differences:
            print(f"  - {diff['message']}")
    
    return result.is_equal
```

### Data Migration Validation

```python
from json_compare_pro import JSONPathExtractor, compare_jsons

def validate_migration(old_data, new_data):
    # Extract specific fields for comparison
    extractor = JSONPathExtractor()
    
    # Compare user data
    old_users = extractor.find(old_data, "$.users[*]")
    new_users = extractor.find(new_data, "$.users[*]")
    
    # Validate each user
    for old_user, new_user in zip(old_users.values, new_users.values):
        result = compare_jsons(
            old_user, new_user,
            keys_to_ignore=["id", "created_at"],  # These change during migration
            custom_validations={
                "email": {"type": "contains", "expected": "@"},
                "status": {"type": "equals", "expected": "active"}
            }
        )
        
        if not result:
            print(f"❌ User migration validation failed")
            return False
    
    print("✅ All users migrated successfully")
    return True
```

### Configuration Management

```python
from json_compare_pro import JSONCompareConfig, ComparisonMode

# Different comparison modes for different scenarios
configs = {
    "strict": JSONCompareConfig(
        comparison_mode=ComparisonMode.STRICT,
        case_sensitive=True,
        ignore_order=False
    ),
    
    "lenient": JSONCompareConfig(
        comparison_mode=ComparisonMode.LENIENT,
        case_sensitive=False,
        ignore_order=True,
        numeric_tolerance=0.1
    ),
    
    "tolerance": JSONCompareConfig(
        comparison_mode=ComparisonMode.TOLERANCE,
        numeric_tolerance=0.01,
        ignore_whitespace=True
    )
}

# Use appropriate config based on context
def compare_with_context(json1, json2, context="strict"):
    config = configs[context]
    return compare_jsons_with_config(json1, json2, config)
```

## 🧪 Testing

### Run Tests

```bash
# Install development dependencies
pip install -e ".[dev]"

# Run all tests
pytest

# Run with coverage
pytest --cov=json_compare_pro --cov-report=html

# Run specific test categories
pytest -m "not slow"
pytest tests/test_core.py::TestBasicComparison
```

### Test Examples

```python
import pytest
from json_compare_pro import compare_jsons

class TestMyData:
    def test_user_data_consistency(self):
        """Test that user data maintains consistency across operations."""
        original = {"name": "John", "age": 30, "email": "john@example.com"}
        processed = {"name": "John", "age": 30, "email": "john@example.com"}
        
        assert compare_jsons(original, processed)
    
    def test_api_response_structure(self):
        """Test API response structure validation."""
        expected = {"status": "success", "data": {"users": []}}
        actual = {"status": "success", "data": {"users": []}}
        
        # Ignore dynamic fields
        result = compare_jsons(
            expected, actual,
            keys_to_ignore=["data.users[*].id", "data.users[*].created_at"]
        )
        
        assert result
```

## 📖 Documentation

- **[Full Documentation](https://json-compare-pro.readthedocs.io)** - Comprehensive API reference and guides
- **[Examples Gallery](https://json-compare-pro.readthedocs.io/en/latest/examples.html)** - Real-world usage examples
- **[Migration Guide](https://json-compare-pro.readthedocs.io/en/latest/migration.html)** - Upgrading from other libraries

## 🤝 Contributing

We welcome contributions! Please see our [Contributing Guide](CONTRIBUTING.md) for details.

### Development Setup

```bash
# Clone the repository
git clone https://github.com/harshitgoel09/json-compare-pro.git
cd json-compare-pro

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -e ".[dev]"

# Run pre-commit hooks
pre-commit install

# Run tests
pytest
```

### Code Quality

```bash
# Format code
black src tests
isort src tests

# Lint code
flake8 src tests
mypy src

# Run all quality checks
tox
```

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- Inspired by the need for robust JSON comparison in API testing
- Built with modern Python best practices
- Thanks to the open-source community for excellent dependencies

## 📞 Support

- **Issues**: [GitHub Issues](https://github.com/harshitgoel09/json-compare-pro/issues)
- **Discussions**: [GitHub Discussions](https://github.com/harshitgoel09/json-compare-pro/discussions)
- **Documentation**: [Read the Docs](https://json-compare-pro.readthedocs.io)

---

**Made with ❤️ by Harshit Goel for the Python community** 