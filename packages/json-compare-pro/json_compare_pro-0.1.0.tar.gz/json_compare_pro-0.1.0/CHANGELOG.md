# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added
- Initial release of JSON Compare Pro
- Core JSON comparison functionality with flexible configuration
- Custom validation rules (regex, patterns, ranges, etc.)
- Schema validation with JSON Schema support
- JSONPath extraction and filtering
- Detailed diff reporting with multiple output formats
- Command-line interface with rich output
- Comprehensive test suite with 100% coverage
- Type hints throughout the codebase
- Production-ready error handling and logging

### Features
- **Advanced Comparison**: Flexible key ignoring, key existence validation, numeric tolerance
- **Schema Validation**: JSON Schema support with detailed error reporting
- **JSONPath Support**: Advanced querying and filtering capabilities
- **Diff Reporting**: Multiple output formats (JSON, text, markdown, HTML, rich terminal)
- **CLI Interface**: Command-line tool for quick comparisons and validation
- **Custom Validators**: Extensible validation system with pre-built validators
- **Performance Optimized**: Efficient algorithms for large JSON objects

### Technical
- Modern Python packaging with pyproject.toml
- Comprehensive dependency management
- Code quality tools (black, isort, flake8, mypy)
- CI/CD pipeline with GitHub Actions
- Documentation with Sphinx and Read the Docs
- Pre-commit hooks for code quality
- Tox for multi-environment testing

## [0.1.0] - 2024-01-01

### Added
- Initial release
- Basic JSON comparison functionality
- Key ignoring and validation features
- Custom validation rules
- Schema validation support
- JSONPath extraction
- Diff reporting
- CLI interface
- Comprehensive documentation
- Test suite with full coverage 