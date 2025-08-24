"""Command-line interface for JSON Compare Pro."""

import json
import sys
from pathlib import Path
from typing import Any, Dict, List, Optional

import click
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.syntax import Syntax
from rich.progress import Progress, SpinnerColumn, TextColumn

from .core import compare_jsons_with_config, JSONCompareConfig, ComparisonMode
from .validators import (
    create_string_validator,
    create_numeric_validator,
    create_range_validator,
    create_list_validator,
    create_type_validator,
    create_function_validator,
    EMAIL_VALIDATOR,
    URL_VALIDATOR,
    UUID_VALIDATOR,
    DATE_VALIDATOR,
    TIMESTAMP_VALIDATOR,
)
from .schema import JSONSchemaValidator, SchemaBuilder
from .jsonpath import JSONPathExtractor, JSONPathQueryBuilder
from .diff import JSONDiffReporter, DiffFormatter
from .exceptions import JSONCompareError, ValidationError, SchemaValidationError, JSONPathError

console = Console()


def load_json_file(file_path: str) -> Dict[str, Any]:
    """Load JSON from file."""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    except FileNotFoundError:
        console.print(f"[red]Error: File '{file_path}' not found.[/red]")
        sys.exit(1)
    except json.JSONDecodeError as e:
        console.print(f"[red]Error: Invalid JSON in '{file_path}': {e}[/red]")
        sys.exit(1)
    except Exception as e:
        console.print(f"[red]Error reading '{file_path}': {e}[/red]")
        sys.exit(1)


def save_json_file(data: Dict[str, Any], file_path: str) -> None:
    """Save JSON to file."""
    try:
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
    except Exception as e:
        console.print(f"[red]Error writing to '{file_path}': {e}[/red]")
        sys.exit(1)


def parse_custom_validations(validations: List[str]) -> Dict[str, Dict[str, Any]]:
    """Parse custom validation rules from command line arguments."""
    result = {}
    
    for validation in validations:
        try:
            # Format: key:type:expected_value
            parts = validation.split(':', 2)
            if len(parts) < 3:
                console.print(f"[yellow]Warning: Invalid validation format '{validation}'. Skipping.[/yellow]")
                continue
            
            key, validation_type, expected = parts
            
            if validation_type in ['startswith', 'endswith', 'contains', 'equals', 'regex']:
                result[key] = {
                    "type": validation_type,
                    "expected": expected
                }
            elif validation_type == 'range':
                # Format: key:range:min:max
                range_parts = expected.split(':')
                if len(range_parts) == 2:
                    min_val, max_val = range_parts
                    result[key] = {
                        "type": "range",
                        "min": float(min_val) if min_val else None,
                        "max": float(max_val) if max_val else None
                    }
                else:
                    console.print(f"[yellow]Warning: Invalid range format '{expected}'. Skipping.[/yellow]")
            else:
                console.print(f"[yellow]Warning: Unknown validation type '{validation_type}'. Skipping.[/yellow]")
                
        except Exception as e:
            console.print(f"[yellow]Warning: Error parsing validation '{validation}': {e}. Skipping.[/yellow]")
    
    return result


def create_validators_from_config(validators: List[str]) -> Dict[str, Any]:
    """Create validators from command line configuration."""
    result = {}
    
    for validator_config in validators:
        try:
            # Format: key:validator_type:params
            parts = validator_config.split(':', 2)
            if len(parts) < 2:
                console.print(f"[yellow]Warning: Invalid validator format '{validator_config}'. Skipping.[/yellow]")
                continue
            
            key, validator_type = parts[0], parts[1]
            params = parts[2] if len(parts) > 2 else ""
            
            if validator_type == 'email':
                result[key] = EMAIL_VALIDATOR
            elif validator_type == 'url':
                result[key] = URL_VALIDATOR
            elif validator_type == 'uuid':
                result[key] = UUID_VALIDATOR
            elif validator_type == 'date':
                result[key] = DATE_VALIDATOR
            elif validator_type == 'timestamp':
                tolerance = float(params) if params else 1.0
                result[key] = TimestampValidator(tolerance)
            elif validator_type == 'numeric':
                tolerance = float(params) if params else 0.0
                result[key] = create_numeric_validator(tolerance)
            elif validator_type == 'string':
                pattern = params if params else ".*"
                result[key] = create_string_validator(pattern)
            else:
                console.print(f"[yellow]Warning: Unknown validator type '{validator_type}'. Skipping.[/yellow]")
                
        except Exception as e:
            console.print(f"[yellow]Warning: Error creating validator '{validator_config}': {e}. Skipping.[/yellow]")
    
    return result


def display_result(result: Any, output_format: str = "rich", output_file: Optional[str] = None) -> None:
    """Display comparison result in the specified format."""
    
    if output_format == "json":
        output_data = result.to_dict() if hasattr(result, 'to_dict') else result
        output_json = json.dumps(output_data, indent=2, default=str)
        
        if output_file:
            save_json_file(output_data, output_file)
        else:
            console.print(output_json)
    
    elif output_format == "text":
        if hasattr(result, 'differences'):
            # Handle JSONCompareResult or DiffReport
            if result.is_equal:
                output_text = "✅ JSON objects are equal"
            else:
                output_text = f"❌ JSON objects are different\n\n"
                output_text += f"Found {len(result.differences)} differences:\n\n"
                for diff in result.differences:
                    if hasattr(diff, 'message'):
                        # DiffItem object
                        output_text += f"• {diff.message}\n"
                    else:
                        # Dictionary
                        output_text += f"• {diff.get('message', 'Unknown difference')}\n"
        else:
            output_text = str(result)
        
        if output_file:
            with open(output_file, 'w', encoding='utf-8') as f:
                f.write(output_text)
        else:
            console.print(output_text)
    
    elif output_format == "markdown":
        if hasattr(result, 'differences'):
            output_md = DiffFormatter.to_markdown(result)
        else:
            output_md = f"# JSON Comparison Result\n\n{str(result)}"
        
        if output_file:
            with open(output_file, 'w', encoding='utf-8') as f:
                f.write(output_md)
        else:
            console.print(output_md)
    
    elif output_format == "html":
        if hasattr(result, 'differences'):
            output_html = DiffFormatter.to_html(result)
        else:
            output_html = f"<html><body><h1>JSON Comparison Result</h1><p>{str(result)}</p></body></html>"
        
        if output_file:
            with open(output_file, 'w', encoding='utf-8') as f:
                f.write(output_html)
        else:
            console.print(output_html)
    
    else:  # rich format
        if hasattr(result, 'differences'):
            display_diff_report(result)
        else:
            display_simple_result(result)


def display_diff_report(result: Any) -> None:
    """Display a diff report in rich format."""
    
    # Summary panel
    summary_text = f"""
    [bold]Comparison Result:[/bold] {'✅ Equal' if result.is_equal else '❌ Different'}
    
    [bold]Statistics:[/bold]
    • Total Differences: {result.summary.get('total_differences', 0)}
    • Execution Time: {result.execution_time:.4f}s
    """
    
    if result.summary.get('type_counts'):
        summary_text += "\n[bold]Difference Types:[/bold]\n"
        for diff_type, count in result.summary['type_counts'].items():
            summary_text += f"• {diff_type}: {count}\n"
    
    console.print(Panel(summary_text, title="Summary", border_style="green" if result.is_equal else "red"))
    
    # Differences table
    if result.differences:
        table = Table(title="Differences", show_header=True, header_style="bold magenta")
        table.add_column("Path", style="cyan", no_wrap=True)
        table.add_column("Type", style="yellow")
        table.add_column("Message", style="white")
        table.add_column("Old Value", style="red")
        table.add_column("New Value", style="green")
        
        for diff in result.differences:
            if hasattr(diff, 'path'):
                # DiffItem object
                table.add_row(
                    diff.path,
                    diff.diff_type.value,
                    diff.message,
                    str(diff.old_value) if diff.old_value is not None else "",
                    str(diff.new_value) if diff.new_value is not None else ""
                )
            else:
                # Dictionary
                table.add_row(
                    diff.get('key', ''),
                    diff.get('type', ''),
                    diff.get('message', ''),
                    str(diff.get('value1', '')) if diff.get('value1') is not None else "",
                    str(diff.get('value2', '')) if diff.get('value2') is not None else ""
                )
        
        console.print(table)


def display_simple_result(result: Any) -> None:
    """Display a simple result in rich format."""
    if isinstance(result, bool):
        status = "✅ Equal" if result else "❌ Different"
        console.print(Panel(status, title="Comparison Result", border_style="green" if result else "red"))
    else:
        console.print(Panel(str(result), title="Result"))


@click.group()
@click.version_option()
def main():
    """JSON Compare Pro - Advanced JSON comparison tool."""
    pass


@main.command()
@click.argument('file1', type=click.Path(exists=True))
@click.argument('file2', type=click.Path(exists=True))
@click.option('--ignore-keys', '-i', multiple=True, help='Keys to ignore during comparison')
@click.option('--check-keys-only', '-c', multiple=True, help='Keys to check for existence only')
@click.option('--custom-validations', '-v', multiple=True, help='Custom validation rules (key:type:expected)')
@click.option('--validators', '-V', multiple=True, help='Custom validators (key:validator_type:params)')
@click.option('--case-sensitive/--no-case-sensitive', default=True, help='Case sensitive string comparison')
@click.option('--ignore-order/--no-ignore-order', default=False, help='Ignore order in arrays')
@click.option('--ignore-whitespace/--no-ignore-whitespace', default=False, help='Ignore whitespace in strings')
@click.option('--numeric-tolerance', '-t', type=float, help='Numeric tolerance for comparison')
@click.option('--max-depth', '-d', type=int, help='Maximum depth for recursive comparison')
@click.option('--fail-fast/--no-fail-fast', default=False, help='Stop on first difference')
@click.option('--output-format', '-f', type=click.Choice(['rich', 'json', 'text', 'markdown', 'html']), default='rich', help='Output format')
@click.option('--output-file', '-o', type=click.Path(), help='Output file path')
@click.option('--verbose', is_flag=True, help='Verbose output')
def compare(
    file1: str,
    file2: str,
    ignore_keys: tuple,
    check_keys_only: tuple,
    custom_validations: tuple,
    validators: tuple,
    case_sensitive: bool,
    ignore_order: bool,
    ignore_whitespace: bool,
    numeric_tolerance: Optional[float],
    max_depth: Optional[int],
    fail_fast: bool,
    output_format: str,
    output_file: Optional[str],
    verbose: bool
):
    """Compare two JSON files."""
    
    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        console=console,
    ) as progress:
        
        task = progress.add_task("Loading JSON files...", total=None)
        
        # Load JSON files
        json1 = load_json_file(file1)
        json2 = load_json_file(file2)
        
        progress.update(task, description="Parsing configuration...")
        
        # Parse custom validations
        custom_validations_dict = parse_custom_validations(custom_validations)
        
        # Create validators
        custom_validators_dict = create_validators_from_config(validators)
        
        # Create configuration
        config = JSONCompareConfig(
            keys_to_ignore=list(ignore_keys),
            check_keys_only=list(check_keys_only),
            custom_validations=custom_validations_dict,
            case_sensitive=case_sensitive,
            ignore_order=ignore_order,
            ignore_whitespace=ignore_whitespace,
            numeric_tolerance=numeric_tolerance,
            max_depth=max_depth,
            fail_fast=fail_fast,
            verbose=verbose,
            custom_validators=custom_validators_dict
        )
        
        progress.update(task, description="Comparing JSON objects...")
        
        # Perform comparison
        try:
            result = compare_jsons_with_config(json1, json2, config)
            
            progress.update(task, description="Generating output...")
            
            # Display result
            display_result(result, output_format, output_file)
            
            # Exit code
            sys.exit(0 if result.is_equal else 1)
            
        except Exception as e:
            console.print(f"[red]Error during comparison: {e}[/red]")
            sys.exit(1)


@main.command()
@click.argument('file1', type=click.Path(exists=True))
@click.argument('file2', type=click.Path(exists=True))
@click.option('--output-format', '-f', type=click.Choice(['rich', 'json', 'text', 'markdown', 'html']), default='rich', help='Output format')
@click.option('--output-file', '-o', type=click.Path(), help='Output file path')
@click.option('--ignore-paths', '-i', multiple=True, help='Paths to ignore during diff generation')
@click.option('--max-depth', '-d', type=int, help='Maximum depth for diff generation')
def diff(
    file1: str,
    file2: str,
    output_format: str,
    output_file: Optional[str],
    ignore_paths: tuple,
    max_depth: Optional[int]
):
    """Generate detailed diff report between two JSON files."""
    
    # Load JSON files
    json1 = load_json_file(file1)
    json2 = load_json_file(file2)
    
    # Create diff reporter
    diff_config = {
        "ignore_paths": list(ignore_paths),
        "max_depth": max_depth,
        "include_metadata": True
    }
    
    reporter = JSONDiffReporter(diff_config)
    
    # Generate diff
    try:
        diff_report = reporter.generate_diff(json1, json2)
        
        # Display result
        display_result(diff_report, output_format, output_file)
        
    except Exception as e:
        console.print(f"[red]Error generating diff: {e}[/red]")
        sys.exit(1)


@main.command()
@click.argument('file', type=click.Path(exists=True))
@click.argument('jsonpath', type=str)
@click.option('--output-format', '-f', type=click.Choice(['rich', 'json', 'text']), default='rich', help='Output format')
@click.option('--output-file', '-o', type=click.Path(), help='Output file path')
def extract(
    file: str,
    jsonpath: str,
    output_format: str,
    output_file: Optional[str]
):
    """Extract values from JSON file using JSONPath expression."""
    
    # Load JSON file
    json_data = load_json_file(file)
    
    # Create JSONPath extractor
    extractor = JSONPathExtractor()
    
    try:
        # Extract values
        result = extractor.find(json_data, jsonpath)
        
        # Display result
        if output_format == "json":
            output_data = {
                "jsonpath": jsonpath,
                "count": result.count,
                "values": result.values,
                "paths": result.paths
            }
            display_result(output_data, output_format, output_file)
        elif output_format == "text":
            output_text = f"JSONPath: {jsonpath}\nCount: {result.count}\n\nValues:\n"
            for i, (value, path) in enumerate(zip(result.values, result.paths)):
                output_text += f"{i+1}. Path: {path}\n   Value: {value}\n\n"
            display_result(output_text, output_format, output_file)
        else:  # rich
            table = Table(title=f"JSONPath Results: {jsonpath}")
            table.add_column("Index", style="cyan")
            table.add_column("Path", style="yellow")
            table.add_column("Value", style="green")
            
            for i, (value, path) in enumerate(zip(result.values, result.paths)):
                table.add_row(str(i+1), path, str(value))
            
            console.print(table)
            console.print(f"\n[bold]Total matches:[/bold] {result.count}")
        
    except Exception as e:
        console.print(f"[red]Error extracting values: {e}[/red]")
        sys.exit(1)


@main.command()
@click.argument('file', type=click.Path(exists=True))
@click.argument('schema_file', type=click.Path(exists=True))
@click.option('--output-format', '-f', type=click.Choice(['rich', 'json', 'text']), default='rich', help='Output format')
@click.option('--output-file', '-o', type=click.Path(), help='Output file path')
def validate(
    file: str,
    schema_file: str,
    output_format: str,
    output_file: Optional[str]
):
    """Validate JSON file against a JSON schema."""
    
    # Load files
    json_data = load_json_file(file)
    schema_data = load_json_file(schema_file)
    
    # Create schema validator
    validator = JSONSchemaValidator(schema_data)
    
    try:
        # Validate
        result = validator.validate(json_data)
        
        # Display result
        if output_format == "json":
            output_data = {
                "is_valid": result.is_valid,
                "errors": result.errors,
                "warnings": result.warnings
            }
            display_result(output_data, output_format, output_file)
        elif output_format == "text":
            output_text = f"Validation Result: {'Valid' if result.is_valid else 'Invalid'}\n\n"
            if result.errors:
                output_text += "Errors:\n"
                for error in result.errors:
                    output_text += f"- {error['message']} at {' -> '.join(map(str, error['path']))}\n"
            if result.warnings:
                output_text += "\nWarnings:\n"
                for warning in result.warnings:
                    output_text += f"- {warning}\n"
            display_result(output_text, output_format, output_file)
        else:  # rich
            status = "✅ Valid" if result.is_valid else "❌ Invalid"
            console.print(Panel(status, title="Schema Validation", border_style="green" if result.is_valid else "red"))
            
            if result.errors:
                table = Table(title="Validation Errors")
                table.add_column("Path", style="cyan")
                table.add_column("Message", style="red")
                table.add_column("Validator", style="yellow")
                
                for error in result.errors:
                    path_str = " -> ".join(map(str, error['path'])) if error['path'] else "root"
                    table.add_row(path_str, error['message'], str(error.get('validator', '')))
                
                console.print(table)
        
        # Exit code
        sys.exit(0 if result.is_valid else 1)
        
    except Exception as e:
        console.print(f"[red]Error during validation: {e}[/red]")
        sys.exit(1)


@main.command()
@click.option('--type', '-t', type=click.Choice(['user', 'product', 'api-response']), help='Pre-built schema type')
@click.option('--output-file', '-o', type=click.Path(), help='Output file path')
def generate_schema(type: Optional[str], output_file: Optional[str]):
    """Generate a JSON schema."""
    
    from .schema import create_user_schema, create_product_schema, create_api_response_schema
    
    try:
        if type == 'user':
            schema = create_user_schema()
        elif type == 'product':
            schema = create_product_schema()
        elif type == 'api-response':
            schema = create_api_response_schema()
        else:
            # Interactive schema builder
            console.print("[yellow]Interactive schema builder not implemented yet. Use --type option.[/yellow]")
            return
        
        # Display or save schema
        if output_file:
            save_json_file(schema, output_file)
            console.print(f"[green]Schema saved to {output_file}[/green]")
        else:
            console.print(Syntax(json.dumps(schema, indent=2), "json", theme="monokai"))
        
    except Exception as e:
        console.print(f"[red]Error generating schema: {e}[/red]")
        sys.exit(1)


if __name__ == '__main__':
    main() 