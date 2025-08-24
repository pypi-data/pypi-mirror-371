"""Core JSON comparison functionality."""

import re
from typing import Any, Dict, List, Optional, Union, Callable
from dataclasses import dataclass, field
from enum import Enum

from .exceptions import ValidationError, JSONCompareError, UnsupportedTypeError


class ComparisonMode(Enum):
    """Enumeration for different comparison modes."""
    STRICT = "strict"
    LENIENT = "lenient"
    SCHEMA_BASED = "schema_based"
    TOLERANCE = "tolerance"


@dataclass
class JSONCompareConfig:
    """Configuration for JSON comparison."""
    
    # Basic comparison settings
    keys_to_ignore: List[str] = field(default_factory=list)
    check_keys_only: List[str] = field(default_factory=list)
    custom_validations: Dict[str, Dict[str, Any]] = field(default_factory=dict)
    
    # Advanced settings
    comparison_mode: ComparisonMode = ComparisonMode.STRICT
    case_sensitive: bool = True
    ignore_order: bool = False
    ignore_whitespace: bool = False
    numeric_tolerance: Optional[float] = None
    max_depth: Optional[int] = None
    
    # Schema validation
    schema: Optional[Dict[str, Any]] = None
    validate_schema: bool = False
    
    # JSONPath settings
    jsonpath_filters: Dict[str, str] = field(default_factory=dict)
    
    # Custom validators
    custom_validators: Dict[str, Callable] = field(default_factory=dict)
    
    # Output settings
    verbose: bool = False
    include_diff: bool = True
    fail_fast: bool = False


@dataclass
class JSONCompareResult:
    """Result of JSON comparison."""
    
    is_equal: bool
    differences: List[Dict[str, Any]] = field(default_factory=list)
    ignored_keys: List[str] = field(default_factory=list)
    validation_errors: List[Dict[str, Any]] = field(default_factory=list)
    execution_time: Optional[float] = None
    config: Optional[JSONCompareConfig] = None
    
    def __bool__(self) -> bool:
        """Return True if comparison was successful."""
        return self.is_equal
    
    def get_summary(self) -> Dict[str, Any]:
        """Get a summary of the comparison result."""
        return {
            "is_equal": self.is_equal,
            "total_differences": len(self.differences),
            "total_ignored_keys": len(self.ignored_keys),
            "total_validation_errors": len(self.validation_errors),
            "execution_time": self.execution_time,
        }
    
    def is_empty(self) -> bool:
        """Check if the result has no differences."""
        return len(self.differences) == 0
    
    @property
    def summary(self) -> Dict[str, Any]:
        """Get a summary of the comparison result."""
        return {
            "is_equal": self.is_equal,
            "total_differences": len(self.differences),
            "total_ignored_keys": len(self.ignored_keys),
            "total_validation_errors": len(self.validation_errors),
            "execution_time": self.execution_time,
        }


def compare_jsons(
    json1: Dict[str, Any],
    json2: Dict[str, Any],
    keys_to_ignore: Optional[List[str]] = None,
    check_keys_only: Optional[List[str]] = None,
    custom_validations: Optional[Dict[str, Dict[str, Any]]] = None,
    **kwargs
) -> bool:
    """
    Compare two JSON objects with basic configuration.
    
    This is a simplified interface for backward compatibility.
    For advanced features, use compare_jsons_with_config().
    """
    config = JSONCompareConfig(
        keys_to_ignore=keys_to_ignore or [],
        check_keys_only=check_keys_only or [],
        custom_validations=custom_validations or {},
        **kwargs
    )
    
    result = compare_jsons_with_config(json1, json2, config)
    return result.is_equal


def compare_jsons_with_config(
    json1: Dict[str, Any],
    json2: Dict[str, Any],
    config: JSONCompareConfig
) -> JSONCompareResult:
    """
    Compare two JSON objects with advanced configuration.
    
    Args:
        json1: First JSON object
        json2: Second JSON object
        config: Comparison configuration
        
    Returns:
        JSONCompareResult with detailed comparison information
    """
    import time
    start_time = time.time()
    
    # Validate inputs
    if not isinstance(json1, dict) or not isinstance(json2, dict):
        raise UnsupportedTypeError(
            "Both json1 and json2 must be dictionaries",
            data_type=f"json1: {type(json1).__name__}, json2: {type(json2).__name__}"
        )
    
    # Initialize result
    result = JSONCompareResult(
        is_equal=True,
        config=config,
        ignored_keys=config.keys_to_ignore.copy()
    )
    
    try:
        # Apply JSONPath filters if specified
        if config.jsonpath_filters:
            json1 = _apply_jsonpath_filters(json1, config.jsonpath_filters)
            json2 = _apply_jsonpath_filters(json2, config.jsonpath_filters)
        
        # Filter out ignored keys
        filtered_json1 = {k: v for k, v in json1.items() if k not in config.keys_to_ignore}
        filtered_json2 = {k: v for k, v in json2.items() if k not in config.keys_to_ignore}
        
        # Check keys-only validation
        for key in config.check_keys_only:
            if key in filtered_json1 and key not in filtered_json2:
                _add_difference(result, f"Key '{key}' is missing in json2", key=key)
                if config.fail_fast:
                    break
            elif key in filtered_json2 and key not in filtered_json1:
                _add_difference(result, f"Key '{key}' is missing in json1", key=key)
                if config.fail_fast:
                    break
        
        # Compare remaining keys
        for key, value1 in filtered_json1.items():
            if key in config.check_keys_only:
                continue
                
            if key not in filtered_json2:
                _add_difference(result, f"Key '{key}' not found in json2", key=key)
                if config.fail_fast:
                    break
                continue
            
            value2 = filtered_json2.get(key)
            
            # Apply custom validation if specified
            if config.custom_validations and key in config.custom_validations:
                if not _apply_custom_validation(key, value1, value2, config.custom_validations[key], config):
                    _add_difference(result, f"Custom validation failed for key '{key}'", key=key, value1=value1, value2=value2)
                    if config.fail_fast:
                        break
                    continue
            
            # Apply custom validators if specified
            if config.custom_validators and key in config.custom_validators:
                validator = config.custom_validators[key]
                if not validator(value1, value2):
                    _add_difference(result, f"Custom validator failed for key '{key}'", key=key, value1=value1, value2=value2)
                    if config.fail_fast:
                        break
                    continue
            
            # Compare values based on type and configuration
            if not _compare_values(key, value1, value2, config, result):
                if config.fail_fast:
                    break
        
        # Check for extra keys in json2
        extra_keys = set(filtered_json2.keys()) - set(filtered_json1.keys())
        extra_keys -= set(config.check_keys_only)
        
        if extra_keys:
            _add_difference(result, f"Extra keys found in json2: {extra_keys}", extra_keys=list(extra_keys))
        
        # Update result
        result.is_equal = len(result.differences) == 0
        
    except Exception as e:
        result.is_equal = False
        _add_difference(result, f"Comparison failed with error: {str(e)}", error=str(e))
    
    finally:
        result.execution_time = time.time() - start_time
    
    return result


def _compare_values(
    key: str,
    value1: Any,
    value2: Any,
    config: JSONCompareConfig,
    result: JSONCompareResult
) -> bool:
    """Compare two values based on their types and configuration."""
    
    # Handle None values
    if value1 is None and value2 is None:
        return True
    elif value1 is None or value2 is None:
        _add_difference(result, f"Values not equal for key '{key}': {value1} != {value2}", key=key, value1=value1, value2=value2)
        return False
    
    # Handle dictionaries
    if isinstance(value1, dict) and isinstance(value2, dict):
        if config.max_depth is not None and config.max_depth <= 0:
            return value1 == value2
        
        nested_config = config
        if config.max_depth is not None:
            nested_config = JSONCompareConfig(
                **{k: v for k, v in config.__dict__.items()},
                max_depth=config.max_depth - 1
            )
        
        nested_result = compare_jsons_with_config(value1, value2, nested_config)
        if not nested_result.is_equal:
            _add_difference(result, f"Recursive comparison failed for key '{key}'", key=key, nested_differences=nested_result.differences)
            return False
        return True
    
    # Handle lists
    elif isinstance(value1, list) and isinstance(value2, list):
        return _compare_lists(key, value1, value2, config, result)
    
    # Handle strings with case sensitivity and whitespace options
    elif isinstance(value1, str) and isinstance(value2, str):
        return _compare_strings(key, value1, value2, config, result)
    
    # Handle numbers with tolerance
    elif isinstance(value1, (int, float)) and isinstance(value2, (int, float)):
        return _compare_numbers(key, value1, value2, config, result)
    
    # Default comparison
    else:
        if value1 != value2:
            _add_difference(result, f"Values not equal for key '{key}': {value1} != {value2}", key=key, value1=value1, value2=value2)
            return False
        return True


def _compare_lists(
    key: str,
    list1: List[Any],
    list2: List[Any],
    config: JSONCompareConfig,
    result: JSONCompareResult
) -> bool:
    """Compare two lists."""
    
    if len(list1) != len(list2):
        _add_difference(result, f"List lengths differ for key '{key}': {len(list1)} != {len(list2)}", key=key, value1=len(list1), value2=len(list2))
        return False
    
    if config.ignore_order:
        # Unordered comparison
        if all(isinstance(item, dict) for item in list1) and all(isinstance(item, dict) for item in list2):
            return _compare_lists_of_dicts(key, list1, list2, config, result)
        elif all(not isinstance(item, dict) for item in list1) and all(not isinstance(item, dict) for item in list2):
            if sorted(list1) != sorted(list2):
                _add_difference(result, f"Lists do not match at key '{key}'", key=key, value1=list1, value2=list2)
                return False
            return True
        else:
            _add_difference(result, f"List structure mismatch at key '{key}'", key=key, value1=list1, value2=list2)
            return False
    else:
        # Ordered comparison
        for i, (item1, item2) in enumerate(zip(list1, list2)):
            if not _compare_values(f"{key}[{i}]", item1, item2, config, result):
                return False
        return True


def _compare_lists_of_dicts(
    key: str,
    list1: List[Dict[str, Any]],
    list2: List[Dict[str, Any]],
    config: JSONCompareConfig,
    result: JSONCompareResult
) -> bool:
    """Compare lists of dictionaries without considering order."""
    
    unmatched = list2[:]
    
    for i, item1 in enumerate(list1):
        match_found = False
        for j, item2 in enumerate(unmatched):
            if compare_jsons_with_config(item1, item2, config).is_equal:
                unmatched.pop(j)
                match_found = True
                break
        
        if not match_found:
            _add_difference(result, f"Item {i} in list '{key}' not found in second list", key=key, value1=item1, value2=list2)
            return False
    
    return True


def _compare_strings(
    key: str,
    str1: str,
    str2: str,
    config: JSONCompareConfig,
    result: JSONCompareResult
) -> bool:
    """Compare two strings with case sensitivity and whitespace options."""
    
    if config.ignore_whitespace:
        str1 = str1.strip()
        str2 = str2.strip()
    
    if not config.case_sensitive:
        str1 = str1.lower()
        str2 = str2.lower()
    
    if str1 != str2:
        _add_difference(result, f"Strings not equal for key '{key}': {str1} != {str2}", key=key, value1=str1, value2=str2)
        return False
    
    return True


def _compare_numbers(
    key: str,
    num1: Union[int, float],
    num2: Union[int, float],
    config: JSONCompareConfig,
    result: JSONCompareResult
) -> bool:
    """Compare two numbers with optional tolerance."""
    
    if config.numeric_tolerance is not None:
        if abs(num1 - num2) > config.numeric_tolerance:
            _add_difference(result, f"Numbers differ by more than tolerance for key '{key}': {num1} != {num2}", key=key, value1=num1, value2=num2, tolerance=config.numeric_tolerance)
            return False
    else:
        if num1 != num2:
            _add_difference(result, f"Numbers not equal for key '{key}': {num1} != {num2}", key=key, value1=num1, value2=num2)
            return False
    
    return True


def _apply_custom_validation(
    key: str,
    value1: Any,
    value2: Any,
    rule: Dict[str, Any],
    config: JSONCompareConfig
) -> bool:
    """Apply custom validation rule."""
    
    rule_type = rule.get("type")
    expected = rule.get("expected")
    
    if rule_type == "startswith":
        return str(value1).startswith(expected) and str(value2).startswith(expected)
    elif rule_type == "endswith":
        return str(value1).endswith(expected) and str(value2).endswith(expected)
    elif rule_type == "contains":
        return expected in str(value1) and expected in str(value2)
    elif rule_type == "equals":
        return value1 == expected and value2 == expected
    elif rule_type == "regex":
        pattern = re.compile(expected)
        return bool(pattern.match(str(value1))) and bool(pattern.match(str(value2)))
    elif rule_type == "range":
        min_val = rule.get("min")
        max_val = rule.get("max")
        return (min_val is None or value1 >= min_val) and (max_val is None or value1 <= max_val) and \
               (min_val is None or value2 >= min_val) and (max_val is None or value2 <= max_val)
    else:
        raise ValidationError(f"Unknown validation type '{rule_type}' for key '{key}'")


def _apply_jsonpath_filters(data: Dict[str, Any], filters: Dict[str, str]) -> Dict[str, Any]:
    """Apply JSONPath filters to data."""
    # This is a placeholder - actual implementation would use jsonpath-ng
    # For now, return the original data
    return data


def _add_difference(result: JSONCompareResult, message: str, **details: Any) -> None:
    """Add a difference to the result."""
    difference = {
        "message": message,
        **details
    }
    result.differences.append(difference) 