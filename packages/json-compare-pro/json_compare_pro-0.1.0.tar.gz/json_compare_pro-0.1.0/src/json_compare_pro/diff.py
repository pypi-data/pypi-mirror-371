"""Diff reporting functionality for JSON comparison."""

import json
from typing import Any, Dict, List, Optional, Union
from dataclasses import dataclass, field
from enum import Enum

from .exceptions import JSONCompareError


class DiffType(Enum):
    """Types of differences."""
    ADDED = "added"
    REMOVED = "removed"
    CHANGED = "changed"
    TYPE_CHANGED = "type_changed"
    STRUCTURE_CHANGED = "structure_changed"


@dataclass
class DiffItem:
    """Represents a single difference between two JSON objects."""
    
    path: str
    diff_type: DiffType
    old_value: Optional[Any] = None
    new_value: Optional[Any] = None
    message: str = ""
    details: Dict[str, Any] = field(default_factory=dict)
    
    def __post_init__(self):
        if not self.message:
            self.message = self._generate_message()
    
    def _generate_message(self) -> str:
        """Generate a human-readable message for this diff."""
        if self.diff_type == DiffType.ADDED:
            return f"Added '{self.path}' with value: {self.new_value}"
        elif self.diff_type == DiffType.REMOVED:
            return f"Removed '{self.path}' with value: {self.old_value}"
        elif self.diff_type == DiffType.CHANGED:
            return f"Changed '{self.path}' from {self.old_value} to {self.new_value}"
        elif self.diff_type == DiffType.TYPE_CHANGED:
            old_type = type(self.old_value).__name__
            new_type = type(self.new_value).__name__
            return f"Type changed for '{self.path}' from {old_type} to {new_type}"
        elif self.diff_type == DiffType.STRUCTURE_CHANGED:
            return f"Structure changed for '{self.path}'"
        else:
            return f"Unknown difference at '{self.path}'"


@dataclass
class DiffReport:
    """Complete diff report between two JSON objects."""
    
    differences: List[DiffItem] = field(default_factory=list)
    summary: Dict[str, Any] = field(default_factory=dict)
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def __post_init__(self):
        self._update_summary()
    
    def _update_summary(self) -> None:
        """Update the summary statistics."""
        total_diffs = len(self.differences)
        type_counts = {}
        
        for diff in self.differences:
            diff_type = diff.diff_type.value
            type_counts[diff_type] = type_counts.get(diff_type, 0) + 1
        
        self.summary = {
            "total_differences": total_diffs,
            "type_counts": type_counts,
            "has_differences": total_diffs > 0,
        }
    
    def add_difference(self, diff: DiffItem) -> None:
        """Add a difference to the report."""
        self.differences.append(diff)
        self._update_summary()
    
    def get_differences_by_type(self, diff_type: DiffType) -> List[DiffItem]:
        """Get all differences of a specific type."""
        return [diff for diff in self.differences if diff.diff_type == diff_type]
    
    def get_differences_by_path(self, path: str) -> List[DiffItem]:
        """Get all differences for a specific path."""
        return [diff for diff in self.differences if diff.path == path]
    
    def get_differences_by_path_prefix(self, prefix: str) -> List[DiffItem]:
        """Get all differences for paths starting with a prefix."""
        return [diff for diff in self.differences if diff.path.startswith(prefix)]
    
    def is_empty(self) -> bool:
        """Check if the diff report is empty."""
        return len(self.differences) == 0
    
    @property
    def is_equal(self) -> bool:
        """Check if the objects are equal (no differences)."""
        return self.is_empty()
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert the diff report to a dictionary."""
        return {
            "differences": [
                {
                    "path": diff.path,
                    "type": diff.diff_type.value,
                    "old_value": diff.old_value,
                    "new_value": diff.new_value,
                    "message": diff.message,
                    "details": diff.details,
                }
                for diff in self.differences
            ],
            "summary": self.summary,
            "metadata": self.metadata,
        }
    
    def to_json(self, **kwargs) -> str:
        """Convert the diff report to JSON string."""
        return json.dumps(self.to_dict(), **kwargs)


class JSONDiffReporter:
    """Generates detailed diff reports between JSON objects."""
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """
        Initialize the diff reporter.
        
        Args:
            config: Configuration for diff reporting
        """
        self.config = config or {}
        self.include_metadata = self.config.get("include_metadata", True)
        self.max_depth = self.config.get("max_depth", None)
        self.ignore_paths = self.config.get("ignore_paths", [])
        self.include_values = self.config.get("include_values", True)
    
    def generate_diff(
        self,
        json1: Dict[str, Any],
        json2: Dict[str, Any],
        path: str = "",
        depth: int = 0
    ) -> DiffReport:
        """
        Generate a detailed diff report between two JSON objects.
        
        Args:
            json1: First JSON object
            json2: Second JSON object
            path: Current path in the JSON structure
            depth: Current depth in the JSON structure
            
        Returns:
            DiffReport with detailed differences
        """
        report = DiffReport()
        
        if self.include_metadata:
            report.metadata = {
                "generator": "JSONDiffReporter",
                "config": self.config,
                "depth": depth,
                "path": path,
            }
        
        # Check if we should ignore this path
        if self._should_ignore_path(path):
            return report
        
        # Check if we've reached max depth
        if self.max_depth is not None and depth >= self.max_depth:
            if json1 != json2:
                report.add_difference(DiffItem(
                    path=path or "root",
                    diff_type=DiffType.STRUCTURE_CHANGED,
                    old_value=json1,
                    new_value=json2,
                    details={"reason": "max_depth_reached"}
                ))
            return report
        
        # Compare the objects
        self._compare_objects(json1, json2, path, depth, report)
        
        return report
    
    def _should_ignore_path(self, path: str) -> bool:
        """Check if a path should be ignored."""
        for ignore_path in self.ignore_paths:
            if path.startswith(ignore_path):
                return True
        return False
    
    def _compare_objects(
        self,
        obj1: Any,
        obj2: Any,
        path: str,
        depth: int,
        report: DiffReport
    ) -> None:
        """Compare two objects and add differences to the report."""
        
        # Handle type changes
        if type(obj1) != type(obj2):
            report.add_difference(DiffItem(
                path=path or "root",
                diff_type=DiffType.TYPE_CHANGED,
                old_value=obj1,
                new_value=obj2,
                details={
                    "old_type": type(obj1).__name__,
                    "new_type": type(obj2).__name__
                }
            ))
            return
        
        # Handle different types
        if isinstance(obj1, dict):
            self._compare_dicts(obj1, obj2, path, depth, report)
        elif isinstance(obj1, list):
            self._compare_lists(obj1, obj2, path, depth, report)
        else:
            # Handle primitive types
            if obj1 != obj2:
                report.add_difference(DiffItem(
                    path=path or "root",
                    diff_type=DiffType.CHANGED,
                    old_value=obj1,
                    new_value=obj2
                ))
    
    def _compare_dicts(
        self,
        dict1: Dict[str, Any],
        dict2: Dict[str, Any],
        path: str,
        depth: int,
        report: DiffReport
    ) -> None:
        """Compare two dictionaries."""
        
        # Find added keys
        for key in dict2:
            if key not in dict1:
                full_path = f"{path}.{key}" if path else key
                if not self._should_ignore_path(full_path):
                    report.add_difference(DiffItem(
                        path=full_path,
                        diff_type=DiffType.ADDED,
                        new_value=dict2[key]
                    ))
        
        # Find removed keys
        for key in dict1:
            if key not in dict2:
                full_path = f"{path}.{key}" if path else key
                if not self._should_ignore_path(full_path):
                    report.add_difference(DiffItem(
                        path=full_path,
                        diff_type=DiffType.REMOVED,
                        old_value=dict1[key]
                    ))
        
        # Compare common keys
        for key in dict1:
            if key in dict2:
                full_path = f"{path}.{key}" if path else key
                if not self._should_ignore_path(full_path):
                    self._compare_objects(
                        dict1[key],
                        dict2[key],
                        full_path,
                        depth + 1,
                        report
                    )
    
    def _compare_lists(
        self,
        list1: List[Any],
        list2: List[Any],
        path: str,
        depth: int,
        report: DiffReport
    ) -> None:
        """Compare two lists."""
        
        # Simple length comparison first
        if len(list1) != len(list2):
            report.add_difference(DiffItem(
                path=path or "root",
                diff_type=DiffType.CHANGED,
                old_value=len(list1),
                new_value=len(list2),
                details={"reason": "length_difference"}
            ))
        
        # Compare elements up to the minimum length
        min_length = min(len(list1), len(list2))
        for i in range(min_length):
            element_path = f"{path}[{i}]" if path else f"[{i}]"
            if not self._should_ignore_path(element_path):
                self._compare_objects(
                    list1[i],
                    list2[i],
                    element_path,
                    depth + 1,
                    report
                )
        
        # Handle extra elements in list2
        for i in range(min_length, len(list2)):
            element_path = f"{path}[{i}]" if path else f"[{i}]"
            if not self._should_ignore_path(element_path):
                report.add_difference(DiffItem(
                    path=element_path,
                    diff_type=DiffType.ADDED,
                    new_value=list2[i]
                ))
        
        # Handle missing elements from list1
        for i in range(min_length, len(list1)):
            element_path = f"{path}[{i}]" if path else f"[{i}]"
            if not self._should_ignore_path(element_path):
                report.add_difference(DiffItem(
                    path=element_path,
                    diff_type=DiffType.REMOVED,
                    old_value=list1[i]
                ))


class DiffFormatter:
    """Formats diff reports in different output formats."""
    
    @staticmethod
    def to_text(report: DiffReport, indent: int = 2) -> str:
        """Format diff report as plain text."""
        lines = []
        
        # Header
        if report.is_empty():
            lines.append("No differences found.")
        else:
            lines.append(f"Found {report.summary['total_differences']} differences:")
            lines.append("")
            
            # Group by type
            for diff_type, count in report.summary['type_counts'].items():
                lines.append(f"{diff_type.upper()} ({count}):")
                type_diffs = report.get_differences_by_type(DiffType(diff_type))
                for diff in type_diffs:
                    lines.append(f"{' ' * indent}• {diff.message}")
                lines.append("")
        
        return "\n".join(lines)
    
    @staticmethod
    def to_markdown(report: DiffReport) -> str:
        """Format diff report as markdown."""
        lines = []
        
        # Header
        lines.append("# JSON Diff Report")
        lines.append("")
        
        if report.is_empty():
            lines.append("✅ **No differences found.**")
        else:
            lines.append(f"❌ **Found {report.summary['total_differences']} differences**")
            lines.append("")
            
            # Summary table
            lines.append("## Summary")
            lines.append("")
            lines.append("| Type | Count |")
            lines.append("|------|-------|")
            for diff_type, count in report.summary['type_counts'].items():
                lines.append(f"| {diff_type} | {count} |")
            lines.append("")
            
            # Detailed differences
            lines.append("## Differences")
            lines.append("")
            
            for diff in report.differences:
                icon = {
                    DiffType.ADDED: "➕",
                    DiffType.REMOVED: "➖",
                    DiffType.CHANGED: "🔄",
                    DiffType.TYPE_CHANGED: "🔄",
                    DiffType.STRUCTURE_CHANGED: "🏗️",
                }.get(diff.diff_type, "❓")
                
                lines.append(f"### {icon} {diff.path}")
                lines.append("")
                lines.append(f"**Type:** {diff.diff_type.value}")
                lines.append("")
                lines.append(f"**Message:** {diff.message}")
                lines.append("")
                
                if diff.old_value is not None:
                    lines.append(f"**Old Value:** `{diff.old_value}`")
                    lines.append("")
                
                if diff.new_value is not None:
                    lines.append(f"**New Value:** `{diff.new_value}`")
                    lines.append("")
                
                if diff.details:
                    lines.append("**Details:**")
                    lines.append("```json")
                    lines.append(json.dumps(diff.details, indent=2))
                    lines.append("```")
                    lines.append("")
        
        return "\n".join(lines)
    
    @staticmethod
    def to_html(report: DiffReport) -> str:
        """Format diff report as HTML."""
        html_lines = []
        
        # HTML header
        html_lines.append("""
<!DOCTYPE html>
<html>
<head>
    <title>JSON Diff Report</title>
    <style>
        body { font-family: Arial, sans-serif; margin: 20px; }
        .diff-item { margin: 10px 0; padding: 10px; border: 1px solid #ddd; border-radius: 5px; }
        .added { background-color: #d4edda; border-color: #c3e6cb; }
        .removed { background-color: #f8d7da; border-color: #f5c6cb; }
        .changed { background-color: #fff3cd; border-color: #ffeaa7; }
        .type-changed { background-color: #d1ecf1; border-color: #bee5eb; }
        .structure-changed { background-color: #e2e3e5; border-color: #d6d8db; }
        .path { font-weight: bold; color: #495057; }
        .message { margin: 5px 0; }
        .values { font-family: monospace; background-color: #f8f9fa; padding: 5px; border-radius: 3px; }
        .summary { background-color: #f8f9fa; padding: 15px; border-radius: 5px; margin: 20px 0; }
    </style>
</head>
<body>
""")
        
        # Title
        html_lines.append("<h1>JSON Diff Report</h1>")
        
        if report.is_empty():
            html_lines.append('<p style="color: green;">✅ <strong>No differences found.</strong></p>')
        else:
            # Summary
            html_lines.append('<div class="summary">')
            html_lines.append(f'<h2>Summary</h2>')
            html_lines.append(f'<p><strong>Total Differences:</strong> {report.summary["total_differences"]}</p>')
            html_lines.append('<ul>')
            for diff_type, count in report.summary['type_counts'].items():
                html_lines.append(f'<li><strong>{diff_type}:</strong> {count}</li>')
            html_lines.append('</ul>')
            html_lines.append('</div>')
            
            # Differences
            html_lines.append('<h2>Differences</h2>')
            
            for diff in report.differences:
                css_class = diff.diff_type.value.replace('_', '-')
                html_lines.append(f'<div class="diff-item {css_class}">')
                html_lines.append(f'<div class="path">{diff.path}</div>')
                html_lines.append(f'<div class="message">{diff.message}</div>')
                
                if diff.old_value is not None:
                    html_lines.append(f'<div><strong>Old Value:</strong> <span class="values">{diff.old_value}</span></div>')
                
                if diff.new_value is not None:
                    html_lines.append(f'<div><strong>New Value:</strong> <span class="values">{diff.new_value}</span></div>')
                
                if diff.details:
                    html_lines.append(f'<div><strong>Details:</strong> <span class="values">{json.dumps(diff.details)}</span></div>')
                
                html_lines.append('</div>')
        
        # HTML footer
        html_lines.append("</body></html>")
        
        return "\n".join(html_lines) 