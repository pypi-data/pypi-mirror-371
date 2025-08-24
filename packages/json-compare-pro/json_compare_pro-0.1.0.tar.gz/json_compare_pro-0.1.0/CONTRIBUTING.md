# Contributing to JSON Compare Pro

Thank you for your interest in contributing to JSON Compare Pro! This document provides guidelines and information for contributors.

## 🤝 How to Contribute

### Types of Contributions

We welcome various types of contributions:

- **Bug Reports**: Report bugs and issues
- **Feature Requests**: Suggest new features and improvements
- **Code Contributions**: Submit pull requests with code changes
- **Documentation**: Improve or add documentation
- **Tests**: Add or improve test coverage
- **Examples**: Create usage examples and tutorials

### Getting Started

1. **Fork the repository** on GitHub
2. **Clone your fork** locally
3. **Create a virtual environment**:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```
4. **Install dependencies**:
   ```bash
   pip install -e ".[dev]"
   ```
5. **Set up pre-commit hooks**:
   ```bash
   pre-commit install
   ```

### Development Workflow

1. **Create a feature branch**:
   ```bash
   git checkout -b feature/your-feature-name
   ```

2. **Make your changes** following the coding standards below

3. **Run tests** to ensure everything works:
   ```bash
   pytest
   pytest --cov=json_compare_pro --cov-report=html
   ```

4. **Run code quality checks**:
   ```bash
   black src tests
   isort src tests
   flake8 src tests
   mypy src
   ```

5. **Commit your changes** with a descriptive message:
   ```bash
   git commit -m "feat: add new validation rule for email addresses"
   ```

6. **Push to your fork** and create a pull request

## 📝 Coding Standards

### Code Style

We use several tools to maintain code quality:

- **Black**: Code formatting
- **isort**: Import sorting
- **flake8**: Linting
- **mypy**: Type checking

Run these tools before submitting your code:

```bash
# Format code
black src tests
isort src tests

# Check code quality
flake8 src tests
mypy src
```

### Type Hints

All new code should include type hints:

```python
from typing import Dict, List, Optional, Any

def compare_jsons(
    json1: Dict[str, Any],
    json2: Dict[str, Any],
    config: Optional[JSONCompareConfig] = None
) -> JSONCompareResult:
    """Compare two JSON objects."""
    pass
```

### Documentation

- **Docstrings**: All public functions and classes should have docstrings
- **Comments**: Add comments for complex logic
- **README**: Update README.md for new features
- **Examples**: Add examples for new functionality

### Testing

- **Test Coverage**: Aim for 100% test coverage for new code
- **Test Types**: Include unit tests, integration tests, and edge cases
- **Test Naming**: Use descriptive test names that explain what is being tested

Example test structure:

```python
def test_new_feature_with_valid_input():
    """Test new feature with valid input data."""
    # Arrange
    input_data = {"test": "data"}
    expected = True
    
    # Act
    result = new_feature(input_data)
    
    # Assert
    assert result == expected

def test_new_feature_with_invalid_input():
    """Test new feature with invalid input data."""
    # Arrange
    input_data = None
    
    # Act & Assert
    with pytest.raises(ValueError):
        new_feature(input_data)
```

## 🐛 Bug Reports

When reporting bugs, please include:

1. **Clear description** of the bug
2. **Steps to reproduce** the issue
3. **Expected behavior** vs actual behavior
4. **Environment details** (Python version, OS, etc.)
5. **Code example** that demonstrates the issue
6. **Error messages** and stack traces

## 💡 Feature Requests

When requesting features, please include:

1. **Clear description** of the feature
2. **Use case** and motivation
3. **Proposed implementation** (if you have ideas)
4. **Examples** of how it would be used
5. **Consideration** of backward compatibility

## 🔄 Pull Request Process

### Before Submitting

1. **Ensure tests pass**:
   ```bash
   pytest
   ```

2. **Check code quality**:
   ```bash
   tox
   ```

3. **Update documentation** for any new features

4. **Add tests** for new functionality

5. **Update CHANGELOG.md** with your changes

### Pull Request Guidelines

1. **Clear title** that describes the change
2. **Detailed description** of what was changed and why
3. **Link to issues** if applicable
4. **Screenshots** for UI changes (if applicable)
5. **Test results** showing that tests pass

### Review Process

1. **Automated checks** must pass (CI/CD pipeline)
2. **Code review** by maintainers
3. **Discussion** of any concerns or suggestions
4. **Approval** and merge

## 📚 Documentation

### Adding Documentation

1. **Docstrings**: Update function and class docstrings
2. **README**: Update README.md for new features
3. **Examples**: Add usage examples
4. **API Docs**: Update API documentation if needed

### Documentation Standards

- Use clear, concise language
- Include code examples
- Explain complex concepts
- Keep documentation up to date

## 🧪 Testing

### Running Tests

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=json_compare_pro --cov-report=html

# Run specific test categories
pytest -m "not slow"
pytest tests/test_core.py::TestBasicComparison

# Run with verbose output
pytest -v
```

### Writing Tests

- **Test naming**: Use descriptive names
- **Test structure**: Follow Arrange-Act-Assert pattern
- **Test isolation**: Each test should be independent
- **Edge cases**: Test boundary conditions and error cases

## 🚀 Release Process

### Versioning

We follow [Semantic Versioning](https://semver.org/):

- **Major version**: Breaking changes
- **Minor version**: New features (backward compatible)
- **Patch version**: Bug fixes (backward compatible)

### Release Checklist

1. **Update version** in `pyproject.toml`
2. **Update CHANGELOG.md** with release notes
3. **Run full test suite** and ensure all tests pass
4. **Update documentation** if needed
5. **Create release** on GitHub
6. **Publish to PyPI** (maintainers only)

## 🤝 Community Guidelines

### Code of Conduct

- **Be respectful** and inclusive
- **Be constructive** in feedback
- **Help others** learn and contribute
- **Follow project conventions**

### Communication

- **GitHub Issues**: For bug reports and feature requests
- **GitHub Discussions**: For questions and general discussion
- **Pull Requests**: For code contributions

## 📞 Getting Help

If you need help contributing:

1. **Check existing issues** and discussions
2. **Read the documentation**
3. **Ask questions** in GitHub Discussions
4. **Open an issue** for specific problems

## 🙏 Recognition

Contributors will be recognized in:

- **README.md** contributors section
- **Release notes** for significant contributions
- **GitHub contributors** page

Thank you for contributing to JSON Compare Pro! 🚀 