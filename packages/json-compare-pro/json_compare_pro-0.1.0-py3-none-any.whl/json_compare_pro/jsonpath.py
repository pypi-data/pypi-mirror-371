"""JSONPath functionality for advanced JSON querying and filtering."""

from typing import Any, Dict, List, Optional, Union
from dataclasses import dataclass

from .exceptions import JSONPathError


@dataclass
class JSONPathResult:
    """Result of JSONPath query."""
    
    values: List[Any]
    paths: List[str]
    count: int
    
    def __post_init__(self):
        self.count = len(self.values)
    
    def first(self) -> Optional[Any]:
        """Get the first value, or None if no values."""
        return self.values[0] if self.values else None
    
    def last(self) -> Optional[Any]:
        """Get the last value, or None if no values."""
        return self.values[-1] if self.values else None
    
    def get(self, index: int = 0) -> Optional[Any]:
        """Get value at specific index."""
        try:
            return self.values[index]
        except IndexError:
            return None
    
    def get_path(self, index: int = 0) -> Optional[str]:
        """Get path at specific index."""
        try:
            return self.paths[index]
        except IndexError:
            return None


class JSONPathExtractor:
    """JSONPath extractor using jsonpath-ng library."""
    
    def __init__(self):
        """Initialize the JSONPath extractor."""
        self._parser = None
        self._load_parser()
    
    def _load_parser(self) -> None:
        """Load the jsonpath-ng parser."""
        try:
            from jsonpath_ng import parse
            self._parser = parse
        except ImportError:
            raise ImportError(
                "jsonpath-ng library is required for JSONPath functionality. "
                "Install it with: pip install jsonpath-ng"
            )
    
    def find(self, data: Dict[str, Any], jsonpath: str) -> JSONPathResult:
        """
        Find values using JSONPath expression.
        
        Args:
            data: JSON data to search
            jsonpath: JSONPath expression
            
        Returns:
            JSONPathResult with found values and paths
        """
        if not self._parser:
            raise JSONPathError("JSONPath parser not loaded")
        
        try:
            jsonpath_expr = self._parser(jsonpath)
            matches = jsonpath_expr.find(data)
            
            values = [match.value for match in matches]
            paths = [str(match.path) for match in matches]
            
            return JSONPathResult(values=values, paths=paths, count=len(values))
            
        except Exception as e:
            raise JSONPathError(f"JSONPath query failed: {str(e)}", jsonpath=jsonpath)
    
    def find_first(self, data: Dict[str, Any], jsonpath: str) -> Optional[Any]:
        """Find the first value matching the JSONPath expression."""
        result = self.find(data, jsonpath)
        return result.first()
    
    def find_all(self, data: Dict[str, Any], jsonpath: str) -> List[Any]:
        """Find all values matching the JSONPath expression."""
        result = self.find(data, jsonpath)
        return result.values
    
    def exists(self, data: Dict[str, Any], jsonpath: str) -> bool:
        """Check if any value exists for the JSONPath expression."""
        result = self.find(data, jsonpath)
        return result.count > 0
    
    def count(self, data: Dict[str, Any], jsonpath: str) -> int:
        """Count the number of values matching the JSONPath expression."""
        result = self.find(data, jsonpath)
        return result.count
    
    def extract_subset(self, data: Dict[str, Any], jsonpath: str) -> Dict[str, Any]:
        """
        Extract a subset of data based on JSONPath expression.
        
        Args:
            data: Original JSON data
            jsonpath: JSONPath expression
            
        Returns:
            Subset of data matching the JSONPath
        """
        result = self.find(data, jsonpath)
        
        if result.count == 0:
            return {}
        elif result.count == 1:
            return result.first()
        else:
            return result.values
    
    def filter_by_path(self, data: Dict[str, Any], jsonpath: str, condition: callable) -> JSONPathResult:
        """
        Filter JSONPath results by a condition function.
        
        Args:
            data: JSON data to search
            jsonpath: JSONPath expression
            condition: Function that takes (value, path) and returns bool
            
        Returns:
            Filtered JSONPathResult
        """
        result = self.find(data, jsonpath)
        
        filtered_values = []
        filtered_paths = []
        
        for value, path in zip(result.values, result.paths):
            if condition(value, path):
                filtered_values.append(value)
                filtered_paths.append(path)
        
        return JSONPathResult(values=filtered_values, paths=filtered_paths, count=len(filtered_values))


class JSONPathQueryBuilder:
    """Builder for constructing JSONPath queries."""
    
    def __init__(self):
        self.parts = []
    
    def root(self) -> 'JSONPathQueryBuilder':
        """Start with root ($)."""
        self.parts = ['$']
        return self
    
    def field(self, name: str) -> 'JSONPathQueryBuilder':
        """Add a field selector."""
        if not self.parts:
            self.parts.append('$')
        self.parts.append(f'.{name}')
        return self
    
    def bracket_field(self, name: str) -> 'JSONPathQueryBuilder':
        """Add a bracket field selector."""
        if not self.parts:
            self.parts.append('$')
        self.parts.append(f"['{name}']")
        return self
    
    def index(self, index: int) -> 'JSONPathQueryBuilder':
        """Add an array index selector."""
        if not self.parts:
            self.parts.append('$')
        self.parts.append(f'[{index}]')
        return self
    
    def slice(self, start: Optional[int] = None, end: Optional[int] = None, step: Optional[int] = None) -> 'JSONPathQueryBuilder':
        """Add an array slice selector."""
        if not self.parts:
            self.parts.append('$')
        
        slice_part = '['
        if start is not None:
            slice_part += str(start)
        slice_part += ':'
        if end is not None:
            slice_part += str(end)
        if step is not None:
            slice_part += f':{step}'
        slice_part += ']'
        
        self.parts.append(slice_part)
        return self
    
    def wildcard(self) -> 'JSONPathQueryBuilder':
        """Add a wildcard selector (*)."""
        if not self.parts:
            self.parts.append('$')
        self.parts.append('.*')
        return self
    
    def recursive_wildcard(self) -> 'JSONPathQueryBuilder':
        """Add a recursive wildcard selector (..*)."""
        if not self.parts:
            self.parts.append('$')
        self.parts.append('..*')
        return self
    
    def filter(self, expression: str) -> 'JSONPathQueryBuilder':
        """Add a filter expression."""
        if not self.parts:
            self.parts.append('$')
        self.parts.append(f'[?({expression})]')
        return self
    
    def union(self, *paths: str) -> 'JSONPathQueryBuilder':
        """Add a union of paths."""
        if not self.parts:
            self.parts.append('$')
        union_part = f"[{','.join(paths)}]"
        self.parts.append(union_part)
        return self
    
    def build(self) -> str:
        """Build the final JSONPath query string."""
        return ''.join(self.parts)


# Common JSONPath patterns
class CommonJSONPaths:
    """Common JSONPath patterns for typical use cases."""
    
    @staticmethod
    def all_fields() -> str:
        """Get all fields at root level."""
        return "$.*"
    
    @staticmethod
    def all_values() -> str:
        """Get all values recursively."""
        return "$..*"
    
    @staticmethod
    def all_arrays() -> str:
        """Get all arrays."""
        return "$..[*]"
    
    @staticmethod
    def all_objects() -> str:
        """Get all objects."""
        return "$..*[?(@.constructor === Object)]"
    
    @staticmethod
    def all_strings() -> str:
        """Get all string values."""
        return "$..*[?(@.constructor === String)]"
    
    @staticmethod
    def all_numbers() -> str:
        """Get all numeric values."""
        return "$..*[?(@.constructor === Number)]"
    
    @staticmethod
    def all_booleans() -> str:
        """Get all boolean values."""
        return "$..*[?(@.constructor === Boolean)]"
    
    @staticmethod
    def all_null_values() -> str:
        """Get all null values."""
        return "$..*[?(@ === null)]"
    
    @staticmethod
    def all_non_null_values() -> str:
        """Get all non-null values."""
        return "$..*[?(@ !== null)]"
    
    @staticmethod
    def all_empty_arrays() -> str:
        """Get all empty arrays."""
        return "$..*[?(@.constructor === Array && @.length === 0)]"
    
    @staticmethod
    def all_empty_objects() -> str:
        """Get all empty objects."""
        return "$..*[?(@.constructor === Object && Object.keys(@).length === 0)]"
    
    @staticmethod
    def all_non_empty_arrays() -> str:
        """Get all non-empty arrays."""
        return "$..*[?(@.constructor === Array && @.length > 0)]"
    
    @staticmethod
    def all_non_empty_objects() -> str:
        """Get all non-empty objects."""
        return "$..*[?(@.constructor === Object && Object.keys(@).length > 0)]"


# Utility functions
def extract_values_by_path(data: Dict[str, Any], jsonpath: str) -> List[Any]:
    """Extract values using JSONPath expression."""
    extractor = JSONPathExtractor()
    return extractor.find_all(data, jsonpath)


def extract_value_by_path(data: Dict[str, Any], jsonpath: str) -> Optional[Any]:
    """Extract the first value using JSONPath expression."""
    extractor = JSONPathExtractor()
    return extractor.find_first(data, jsonpath)


def path_exists(data: Dict[str, Any], jsonpath: str) -> bool:
    """Check if a JSONPath exists in the data."""
    extractor = JSONPathExtractor()
    return extractor.exists(data, jsonpath)


def count_by_path(data: Dict[str, Any], jsonpath: str) -> int:
    """Count values matching a JSONPath expression."""
    extractor = JSONPathExtractor()
    return extractor.count(data, jsonpath) 