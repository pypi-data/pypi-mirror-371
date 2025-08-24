# JSON Compare Pro Documentation

Welcome to the documentation for **JSON Compare Pro** - an advanced JSON comparison library with flexible validation rules, schema support, and comprehensive testing capabilities.

## Quick Start

```python
from json_compare_pro import compare_jsons

# Simple comparison
json1 = {"name": "John", "age": 30}
json2 = {"name": "John", "age": 30}

result = compare_jsons(json1, json2)
print(result)  # True
```

## Features

- **Advanced Comparison**: Flexible key ignoring, custom validation rules
- **Schema Validation**: JSON Schema support with detailed error reporting
- **JSONPath Support**: Advanced querying and filtering capabilities
- **Diff Reporting**: Multiple output formats (JSON, text, markdown, HTML)
- **CLI Interface**: Command-line tool for quick comparisons
- **Production Ready**: Comprehensive testing and error handling

## Table of Contents

```{toctree}
:maxdepth: 2
:caption: Contents:

installation
quickstart
api
cli
examples
contributing
changelog
```

## Indices and tables

* {ref}`genindex`
* {ref}`modindex`
* {ref}`search` 