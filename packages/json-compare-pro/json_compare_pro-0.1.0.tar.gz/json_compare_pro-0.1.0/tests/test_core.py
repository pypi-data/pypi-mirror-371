"""Tests for core JSON comparison functionality."""

import pytest
from typing import Dict, Any

from json_compare_pro.core import (
    compare_jsons,
    compare_jsons_with_config,
    JSONCompareConfig,
    JSONCompareResult,
    ComparisonMode,
)
from json_compare_pro.exceptions import UnsupportedTypeError, ValidationError


class TestBasicComparison:
    """Test basic JSON comparison functionality."""
    
    def test_simple_equal_objects(self):
        """Test comparison of simple equal objects."""
        json1 = {"name": "John", "age": 30}
        json2 = {"name": "John", "age": 30}
        
        result = compare_jsons(json1, json2)
        assert result is True
    
    def test_simple_different_objects(self):
        """Test comparison of simple different objects."""
        json1 = {"name": "John", "age": 30}
        json2 = {"name": "Jane", "age": 30}
        
        result = compare_jsons(json1, json2)
        assert result is False
    
    def test_nested_objects(self):
        """Test comparison of nested objects."""
        json1 = {
            "user": {
                "name": "John",
                "address": {
                    "city": "New York",
                    "country": "USA"
                }
            }
        }
        json2 = {
            "user": {
                "name": "John",
                "address": {
                    "city": "New York",
                    "country": "USA"
                }
            }
        }
        
        result = compare_jsons(json1, json2)
        assert result is True
    
    def test_arrays(self):
        """Test comparison of arrays."""
        json1 = {"items": [1, 2, 3]}
        json2 = {"items": [1, 2, 3]}
        
        result = compare_jsons(json1, json2)
        assert result is True
    
    def test_arrays_different_order(self):
        """Test comparison of arrays with different order."""
        json1 = {"items": [1, 2, 3]}
        json2 = {"items": [3, 1, 2]}
        
        result = compare_jsons(json1, json2)
        assert result is False
    
    def test_invalid_inputs(self):
        """Test handling of invalid inputs."""
        with pytest.raises(UnsupportedTypeError):
            compare_jsons("not a dict", {"valid": "dict"})
        
        with pytest.raises(UnsupportedTypeError):
            compare_jsons({"valid": "dict"}, "not a dict")


class TestIgnoredKeys:
    """Test functionality for ignoring keys."""
    
    def test_ignore_single_key(self):
        """Test ignoring a single key."""
        json1 = {"name": "John", "age": 30, "id": "123"}
        json2 = {"name": "John", "age": 25, "id": "456"}
        
        result = compare_jsons(json1, json2, keys_to_ignore=["id"])
        assert result is False  # age is still different
        
        result = compare_jsons(json1, json2, keys_to_ignore=["id", "age"])
        assert result is True
    
    def test_ignore_multiple_keys(self):
        """Test ignoring multiple keys."""
        json1 = {"name": "John", "age": 30, "id": "123", "timestamp": "2023-01-01"}
        json2 = {"name": "John", "age": 25, "id": "456", "timestamp": "2023-01-02"}
        
        result = compare_jsons(json1, json2, keys_to_ignore=["id", "timestamp", "age"])
        assert result is True
    
    def test_ignore_nested_keys(self):
        """Test ignoring nested keys."""
        json1 = {
            "user": {
                "name": "John",
                "age": 30,
                "metadata": {"id": "123", "version": "1.0"}
            }
        }
        json2 = {
            "user": {
                "name": "John",
                "age": 30,
                "metadata": {"id": "456", "version": "2.0"}
            }
        }
        
        result = compare_jsons(json1, json2, keys_to_ignore=["user.metadata.id", "user.metadata.version"])
        assert result is True


class TestKeysOnlyValidation:
    """Test functionality for checking key existence only."""
    
    def test_check_keys_only(self):
        """Test checking keys for existence only."""
        json1 = {"name": "John", "age": 30, "id": "123"}
        json2 = {"name": "Jane", "age": 25, "id": "456"}
        
        result = compare_jsons(json1, json2, check_keys_only=["name", "age"])
        assert result is True  # Keys exist in both, values are ignored
    
    def test_missing_key_in_second(self):
        """Test when a key is missing in the second object."""
        json1 = {"name": "John", "age": 30, "id": "123"}
        json2 = {"name": "Jane", "age": 25}
        
        result = compare_jsons(json1, json2, check_keys_only=["name", "age", "id"])
        assert result is False  # id is missing in json2
    
    def test_missing_key_in_first(self):
        """Test when a key is missing in the first object."""
        json1 = {"name": "John", "age": 30}
        json2 = {"name": "Jane", "age": 25, "id": "456"}
        
        result = compare_jsons(json1, json2, check_keys_only=["name", "age", "id"])
        assert result is False  # id is missing in json1


class TestCustomValidations:
    """Test custom validation functionality."""
    
    def test_startswith_validation(self):
        """Test startswith validation."""
        json1 = {"email": "john@example.com"}
        json2 = {"email": "jane@example.com"}
        
        result = compare_jsons(
            json1, json2,
            custom_validations={"email": {"type": "startswith", "expected": "j"}}
        )
        assert result is True
    
    def test_endswith_validation(self):
        """Test endswith validation."""
        json1 = {"email": "john@example.com"}
        json2 = {"email": "jane@example.com"}
        
        result = compare_jsons(
            json1, json2,
            custom_validations={"email": {"type": "endswith", "expected": ".com"}}
        )
        assert result is True
    
    def test_contains_validation(self):
        """Test contains validation."""
        json1 = {"email": "john@example.com"}
        json2 = {"email": "jane@example.com"}
        
        result = compare_jsons(
            json1, json2,
            custom_validations={"email": {"type": "contains", "expected": "@"}}
        )
        assert result is True
    
    def test_equals_validation(self):
        """Test equals validation."""
        json1 = {"status": "active"}
        json2 = {"status": "active"}
        
        result = compare_jsons(
            json1, json2,
            custom_validations={"status": {"type": "equals", "expected": "active"}}
        )
        assert result is True
    
    def test_regex_validation(self):
        """Test regex validation."""
        json1 = {"phone": "123-456-7890"}
        json2 = {"phone": "987-654-3210"}
        
        result = compare_jsons(
            json1, json2,
            custom_validations={"phone": {"type": "regex", "expected": r"\d{3}-\d{3}-\d{4}"}}
        )
        assert result is True
    
    def test_range_validation(self):
        """Test range validation."""
        json1 = {"score": 85}
        json2 = {"score": 92}
        
        result = compare_jsons(
            json1, json2,
            custom_validations={"score": {"type": "range", "min": 0, "max": 100}}
        )
        assert result is True
    
    def test_invalid_validation_type(self):
        """Test handling of invalid validation type."""
        json1 = {"value": "test"}
        json2 = {"value": "test"}
        
        with pytest.raises(ValidationError):
            compare_jsons(
                json1, json2,
                custom_validations={"value": {"type": "invalid_type", "expected": "test"}}
            )


class TestAdvancedConfiguration:
    """Test advanced configuration options."""
    
    def test_case_insensitive_comparison(self):
        """Test case insensitive string comparison."""
        json1 = {"name": "John", "email": "JOHN@EXAMPLE.COM"}
        json2 = {"name": "john", "email": "john@example.com"}
        
        config = JSONCompareConfig(case_sensitive=False)
        result = compare_jsons_with_config(json1, json2, config)
        assert result.is_equal is True
    
    def test_ignore_whitespace(self):
        """Test ignoring whitespace in strings."""
        json1 = {"message": "Hello World"}
        json2 = {"message": "  Hello World  "}
        
        config = JSONCompareConfig(ignore_whitespace=True)
        result = compare_jsons_with_config(json1, json2, config)
        assert result.is_equal is True
    
    def test_numeric_tolerance(self):
        """Test numeric tolerance comparison."""
        json1 = {"price": 10.0}
        json2 = {"price": 10.1}
        
        config = JSONCompareConfig(numeric_tolerance=0.2)
        result = compare_jsons_with_config(json1, json2, config)
        assert result.is_equal is True
        
        config = JSONCompareConfig(numeric_tolerance=0.05)
        result = compare_jsons_with_config(json1, json2, config)
        assert result.is_equal is False
    
    def test_ignore_order_in_arrays(self):
        """Test ignoring order in arrays."""
        json1 = {"items": [1, 2, 3]}
        json2 = {"items": [3, 1, 2]}
        
        config = JSONCompareConfig(ignore_order=True)
        result = compare_jsons_with_config(json1, json2, config)
        assert result.is_equal is True
    
    def test_max_depth(self):
        """Test maximum depth limitation."""
        json1 = {
            "level1": {
                "level2": {
                    "level3": {"value": "deep"}
                }
            }
        }
        json2 = {
            "level1": {
                "level2": {
                    "level3": {"value": "different"}
                }
            }
        }
        
        config = JSONCompareConfig(max_depth=2)
        result = compare_jsons_with_config(json1, json2, config)
        assert result.is_equal is True  # Differences beyond depth 2 are ignored
    
    def test_fail_fast(self):
        """Test fail fast behavior."""
        json1 = {"a": 1, "b": 2, "c": 3}
        json2 = {"a": 1, "b": 5, "c": 6}
        
        config = JSONCompareConfig(fail_fast=True)
        result = compare_jsons_with_config(json1, json2, config)
        assert result.is_equal is False
        assert len(result.differences) == 1  # Only first difference is recorded


class TestResultObject:
    """Test JSONCompareResult functionality."""
    
    def test_result_boolean_conversion(self):
        """Test boolean conversion of result."""
        json1 = {"a": 1}
        json2 = {"a": 1}
        
        config = JSONCompareConfig()
        result = compare_jsons_with_config(json1, json2, config)
        assert bool(result) is True
        
        json2 = {"a": 2}
        result = compare_jsons_with_config(json1, json2, config)
        assert bool(result) is False
    
    def test_result_summary(self):
        """Test result summary generation."""
        json1 = {"a": 1, "b": 2}
        json2 = {"a": 1, "b": 3}
        
        config = JSONCompareConfig()
        result = compare_jsons_with_config(json1, json2, config)
        
        summary = result.get_summary()
        assert summary["is_equal"] is False
        assert summary["total_differences"] == 1
        assert "execution_time" in summary
    
    def test_result_details(self):
        """Test result details."""
        json1 = {"name": "John", "age": 30}
        json2 = {"name": "Jane", "age": 30}
        
        config = JSONCompareConfig()
        result = compare_jsons_with_config(json1, json2, config)
        
        assert result.is_equal is False
        assert len(result.differences) == 1
        assert result.differences[0]["key"] == "name"
        assert result.differences[0]["value1"] == "John"
        assert result.differences[0]["value2"] == "Jane"


class TestEdgeCases:
    """Test edge cases and error conditions."""
    
    def test_empty_objects(self):
        """Test comparison of empty objects."""
        json1 = {}
        json2 = {}
        
        result = compare_jsons(json1, json2)
        assert result is True
    
    def test_none_values(self):
        """Test handling of None values."""
        json1 = {"value": None}
        json2 = {"value": None}
        
        result = compare_jsons(json1, json2)
        assert result is True
        
        json2 = {"value": "not none"}
        result = compare_jsons(json1, json2)
        assert result is False
    
    def test_mixed_types(self):
        """Test handling of mixed type comparisons."""
        json1 = {"value": "string"}
        json2 = {"value": 123}
        
        result = compare_jsons(json1, json2)
        assert result is False
    
    def test_large_numbers(self):
        """Test handling of large numbers."""
        json1 = {"large": 999999999999999999}
        json2 = {"large": 999999999999999999}
        
        result = compare_jsons(json1, json2)
        assert result is True
    
    def test_floating_point_precision(self):
        """Test floating point precision handling."""
        json1 = {"float": 0.1 + 0.2}
        json2 = {"float": 0.3}
        
        result = compare_jsons(json1, json2)
        # This should be False due to floating point precision
        assert result is False
        
        # With tolerance
        config = JSONCompareConfig(numeric_tolerance=1e-10)
        result = compare_jsons_with_config(json1, json2, config)
        assert result.is_equal is True


class TestPerformance:
    """Test performance characteristics."""
    
    def test_large_object_comparison(self):
        """Test comparison of large objects."""
        # Create large nested objects
        json1 = self._create_large_object(1000)
        json2 = self._create_large_object(1000)
        
        config = JSONCompareConfig()
        result = compare_jsons_with_config(json1, json2, config)
        assert result.is_equal is True
        assert result.execution_time is not None
        assert result.execution_time > 0
    
    def _create_large_object(self, size: int) -> Dict[str, Any]:
        """Create a large object for testing."""
        obj = {}
        for i in range(size):
            obj[f"key_{i}"] = {
                "value": i,
                "nested": {
                    "deep": f"value_{i}",
                    "array": list(range(i % 10))
                }
            }
        return obj 