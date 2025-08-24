"""Custom validators for JSON comparison."""

import re
from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional, Union, Callable
from dataclasses import dataclass

from .exceptions import ValidationError


class CustomValidator(ABC):
    """Abstract base class for custom validators."""
    
    @abstractmethod
    def validate(self, value1: Any, value2: Any) -> bool:
        """Validate two values and return True if they pass validation."""
        pass
    
    def __call__(self, value1: Any, value2: Any) -> bool:
        """Make the validator callable."""
        return self.validate(value1, value2)


@dataclass
class StringPatternValidator(CustomValidator):
    """Validator for string pattern matching."""
    
    pattern: str
    pattern_type: str = "regex"  # regex, startswith, endswith, contains
    case_sensitive: bool = True
    
    def validate(self, value1: Any, value2: Any) -> bool:
        """Validate that both values match the specified pattern."""
        str1 = str(value1)
        str2 = str(value2)
        
        if not self.case_sensitive:
            str1 = str1.lower()
            str2 = str2.lower()
            pattern = self.pattern.lower()
        else:
            pattern = self.pattern
        
        if self.pattern_type == "regex":
            regex = re.compile(pattern)
            return bool(regex.match(str1)) and bool(regex.match(str2))
        elif self.pattern_type == "startswith":
            return str1.startswith(pattern) and str2.startswith(pattern)
        elif self.pattern_type == "endswith":
            return str1.endswith(pattern) and str2.endswith(pattern)
        elif self.pattern_type == "contains":
            return pattern in str1 and pattern in str2
        else:
            raise ValidationError(f"Unknown pattern type: {self.pattern_type}")


@dataclass
class NumericToleranceValidator(CustomValidator):
    """Validator for numeric values with tolerance."""
    
    tolerance: float
    relative_tolerance: bool = False
    
    def validate(self, value1: Any, value2: Any) -> bool:
        """Validate that two numeric values are within tolerance."""
        try:
            num1 = float(value1)
            num2 = float(value2)
        except (ValueError, TypeError):
            return False
        
        if self.relative_tolerance:
            if num1 == 0 and num2 == 0:
                return True
            elif num1 == 0 or num2 == 0:
                return abs(num1 - num2) <= self.tolerance
            else:
                relative_diff = abs(num1 - num2) / max(abs(num1), abs(num2))
                return relative_diff <= self.tolerance
        else:
            return abs(num1 - num2) <= self.tolerance


@dataclass
class RangeValidator(CustomValidator):
    """Validator for values within a specified range."""
    
    min_value: Optional[Union[int, float]] = None
    max_value: Optional[Union[int, float]] = None
    inclusive: bool = True
    
    def validate(self, value1: Any, value2: Any) -> bool:
        """Validate that both values are within the specified range."""
        try:
            num1 = float(value1)
            num2 = float(value2)
        except (ValueError, TypeError):
            return False
        
        if self.inclusive:
            in_range1 = (self.min_value is None or num1 >= self.min_value) and \
                       (self.max_value is None or num1 <= self.max_value)
            in_range2 = (self.min_value is None or num2 >= self.min_value) and \
                       (self.max_value is None or num2 <= self.max_value)
        else:
            in_range1 = (self.min_value is None or num1 > self.min_value) and \
                       (self.max_value is None or num1 < self.max_value)
            in_range2 = (self.min_value is None or num2 > self.min_value) and \
                       (self.max_value is None or num2 < self.max_value)
        
        return in_range1 and in_range2


@dataclass
class ListValidator(CustomValidator):
    """Validator for list comparisons."""
    
    ignore_order: bool = False
    ignore_duplicates: bool = False
    min_length: Optional[int] = None
    max_length: Optional[int] = None
    
    def validate(self, value1: Any, value2: Any) -> bool:
        """Validate that two lists meet the specified criteria."""
        if not isinstance(value1, list) or not isinstance(value2, list):
            return False
        
        # Check length constraints
        if self.min_length is not None and (len(value1) < self.min_length or len(value2) < self.min_length):
            return False
        
        if self.max_length is not None and (len(value1) > self.max_length or len(value2) > self.max_length):
            return False
        
        # Handle duplicates
        list1 = value1.copy()
        list2 = value2.copy()
        
        if self.ignore_duplicates:
            list1 = list(dict.fromkeys(list1))  # Preserve order
            list2 = list(dict.fromkeys(list2))
        
        # Compare lists
        if self.ignore_order:
            return sorted(list1) == sorted(list2)
        else:
            return list1 == list2


@dataclass
class TypeValidator(CustomValidator):
    """Validator for type checking."""
    
    expected_type: Union[type, List[type]]
    
    def validate(self, value1: Any, value2: Any) -> bool:
        """Validate that both values are of the expected type(s)."""
        if isinstance(self.expected_type, list):
            return any(isinstance(value1, t) for t in self.expected_type) and \
                   any(isinstance(value2, t) for t in self.expected_type)
        else:
            return isinstance(value1, self.expected_type) and isinstance(value2, self.expected_type)


@dataclass
class FunctionValidator(CustomValidator):
    """Validator that uses a custom function."""
    
    validation_func: Callable[[Any, Any], bool]
    description: str = "Custom function validation"
    
    def validate(self, value1: Any, value2: Any) -> bool:
        """Validate using the provided function."""
        try:
            return self.validation_func(value1, value2)
        except Exception as e:
            raise ValidationError(f"Custom validation function failed: {str(e)}")


class RegexValidator(StringPatternValidator):
    """Validator for regex pattern matching."""
    
    def __init__(self, pattern: str, case_sensitive: bool = True):
        super().__init__(pattern, "regex", case_sensitive)


class EmailValidator(StringPatternValidator):
    """Validator for email addresses."""
    
    def __init__(self):
        email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        super().__init__(email_pattern, "regex", case_sensitive=False)


class URLValidator(StringPatternValidator):
    """Validator for URLs."""
    
    def __init__(self):
        url_pattern = r'^https?://[^\s/$.?#].[^\s]*$'
        super().__init__(url_pattern, "regex", case_sensitive=False)


class UUIDValidator(StringPatternValidator):
    """Validator for UUID strings."""
    
    def __init__(self):
        uuid_pattern = r'^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$'
        super().__init__(uuid_pattern, "regex", case_sensitive=False)


class DateValidator(StringPatternValidator):
    """Validator for date strings."""
    
    def __init__(self, date_format: str = r'\d{4}-\d{2}-\d{2}'):
        super().__init__(date_format, "regex", case_sensitive=True)


class TimestampValidator(NumericToleranceValidator):
    """Validator for timestamp values with tolerance."""
    
    def __init__(self, tolerance_seconds: float = 1.0):
        super().__init__(tolerance_seconds, relative_tolerance=False)


# Factory functions for common validators
def create_string_validator(pattern: str, pattern_type: str = "regex", **kwargs) -> StringPatternValidator:
    """Create a string pattern validator."""
    return StringPatternValidator(pattern, pattern_type, **kwargs)


def create_numeric_validator(tolerance: float, relative: bool = False) -> NumericToleranceValidator:
    """Create a numeric tolerance validator."""
    return NumericToleranceValidator(tolerance, relative)


def create_range_validator(min_val: Optional[float] = None, max_val: Optional[float] = None, **kwargs) -> RangeValidator:
    """Create a range validator."""
    return RangeValidator(min_val, max_val, **kwargs)


def create_list_validator(**kwargs) -> ListValidator:
    """Create a list validator."""
    return ListValidator(**kwargs)


def create_type_validator(expected_type: Union[type, List[type]]) -> TypeValidator:
    """Create a type validator."""
    return TypeValidator(expected_type)


def create_function_validator(func: Callable[[Any, Any], bool], description: str = "") -> FunctionValidator:
    """Create a function validator."""
    return FunctionValidator(func, description)


# Pre-built validators
EMAIL_VALIDATOR = EmailValidator()
URL_VALIDATOR = URLValidator()
UUID_VALIDATOR = UUIDValidator()
DATE_VALIDATOR = DateValidator()
TIMESTAMP_VALIDATOR = TimestampValidator() 