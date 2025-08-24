# Publishing Guide for JSON Compare Pro

This guide explains how to publish JSON Compare Pro to PyPI and manage releases.

## Prerequisites

1. **PyPI Account**: Create an account on [PyPI](https://pypi.org/account/register/)
2. **TestPyPI Account**: Create an account on [TestPyPI](https://test.pypi.org/account/register/) for testing
3. **API Tokens**: Generate API tokens for both PyPI and TestPyPI
4. **Build Tools**: Install required build tools

```bash
pip install build twine
```

## Development Setup

### 1. Install Development Dependencies

```bash
pip install -e ".[dev]"
```

### 2. Set Up Pre-commit Hooks

```bash
pre-commit install
```

### 3. Configure API Tokens

Create a `~/.pypirc` file:

```ini
[distutils]
index-servers =
    pypi
    testpypi

[pypi]
repository = https://upload.pypi.org/legacy/
username = __token__
password = pypi-your-api-token-here

[testpypi]
repository = https://test.pypi.org/legacy/
username = __token__
password = pypi-your-test-api-token-here
```

## Release Process

### 1. Update Version

Update the version in `pyproject.toml`:

```toml
[project]
version = "0.1.1"  # Increment version number
```

### 2. Update Changelog

Add release notes to `CHANGELOG.md`:

```markdown
## [0.1.1] - 2024-01-15

### Added
- New feature X
- Enhanced functionality Y

### Fixed
- Bug fix Z

### Changed
- Improved performance
```

### 3. Run Quality Checks

```bash
# Run tests
pytest

# Run linting
black --check src tests
isort --check-only src tests
flake8 src tests
mypy src

# Run security checks
bandit -r src/
safety check
```

### 4. Build Distribution

```bash
# Clean previous builds
rm -rf dist/ build/ *.egg-info/

# Build package
python -m build
```

### 5. Test on TestPyPI

```bash
# Upload to TestPyPI
twine upload --repository testpypi dist/*

# Test installation
pip install --index-url https://test.pypi.org/simple/ json-compare-pro
```

### 6. Publish to PyPI

```bash
# Upload to PyPI
twine upload dist/*
```

### 7. Create GitHub Release

1. Go to GitHub repository
2. Click "Releases" → "Create a new release"
3. Tag version: `v0.1.1`
4. Title: `Release v0.1.1`
5. Description: Copy from CHANGELOG.md
6. Upload distribution files (optional)

## Automated Publishing

### GitHub Actions Workflow

Create `.github/workflows/publish.yml`:

```yaml
name: Publish to PyPI

on:
  release:
    types: [published]

jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
    - uses: actions/checkout@v4
    
    - name: Set up Python
      uses: actions/setup-python@v4
      with:
        python-version: '3.11'
    
    - name: Install dependencies
      run: |
        python -m pip install --upgrade pip
        pip install build twine
    
    - name: Build package
      run: python -m build
    
    - name: Publish to PyPI
      env:
        TWINE_USERNAME: __token__
        TWINE_PASSWORD: ${{ secrets.PYPI_API_TOKEN }}
      run: twine upload dist/*
```

### Secrets Setup

1. Go to repository Settings → Secrets and variables → Actions
2. Add `PYPI_API_TOKEN` with your PyPI API token

## Version Management

### Semantic Versioning

Follow [Semantic Versioning](https://semver.org/):

- **MAJOR**: Breaking changes
- **MINOR**: New features (backward compatible)
- **PATCH**: Bug fixes (backward compatible)

### Version Bumping

Use `bump2version` for automated version management:

```bash
pip install bump2version

# Bump patch version (0.1.0 → 0.1.1)
bump2version patch

# Bump minor version (0.1.0 → 0.2.0)
bump2version minor

# Bump major version (0.1.0 → 1.0.0)
bump2version major
```

## Package Configuration

### pyproject.toml

Ensure your `pyproject.toml` has all required fields:

```toml
[project]
name = "json-compare-pro"
version = "0.1.0"
description = "Advanced JSON comparison library with flexible validation rules"
readme = "README.md"
license = {text = "MIT"}
authors = [
    {name = "Your Name", email = "your.email@example.com"},
]
maintainers = [
    {name = "Your Name", email = "your.email@example.com"},
]
keywords = ["json", "comparison", "validation", "testing"]
classifiers = [
    "Development Status :: 4 - Beta",
    "Intended Audience :: Developers",
    "License :: OSI Approved :: MIT License",
    "Operating System :: OS Independent",
    "Programming Language :: Python :: 3",
    "Programming Language :: Python :: 3.8",
    "Programming Language :: Python :: 3.9",
    "Programming Language :: Python :: 3.10",
    "Programming Language :: Python :: 3.11",
    "Programming Language :: Python :: 3.12",
]
requires-python = ">=3.8"
dependencies = [
    "jsonschema>=4.0.0",
    "jsonpath-ng>=1.5.0",
    "deepdiff>=6.0.0",
    "pydantic>=2.0.0",
    "typing-extensions>=4.0.0",
]

[project.urls]
Homepage = "https://github.com/yourusername/json-compare-pro"
Documentation = "https://json-compare-pro.readthedocs.io"
Repository = "https://github.com/yourusername/json-compare-pro.git"
"Bug Tracker" = "https://github.com/yourusername/json-compare-pro/issues"
```

## Troubleshooting

### Common Issues

1. **Authentication Error**
   - Verify API token is correct
   - Check `~/.pypirc` configuration

2. **Package Already Exists**
   - Increment version number
   - Remove old distribution files

3. **Build Errors**
   - Check for syntax errors
   - Verify all dependencies are listed

4. **Import Errors**
   - Test package installation locally
   - Check `__init__.py` files

### Testing Before Release

```bash
# Test build
python -m build

# Test installation
pip install dist/*.whl

# Test functionality
python -c "import json_compare_pro; print(json_compare_pro.__version__)"
```

## Maintenance

### Regular Tasks

1. **Update Dependencies**
   ```bash
   pip install --upgrade pip-tools
   pip-compile --upgrade
   ```

2. **Security Updates**
   ```bash
   safety check
   pip install --upgrade safety
   ```

3. **Documentation Updates**
   - Update README.md
   - Update API documentation
   - Update examples

### Monitoring

- Monitor PyPI download statistics
- Check GitHub issues and discussions
- Review security advisories
- Monitor dependency updates

## Best Practices

1. **Always test on TestPyPI first**
2. **Use semantic versioning consistently**
3. **Keep changelog up to date**
4. **Test installation in clean environment**
5. **Monitor for issues after release**
6. **Respond to user feedback promptly**

## Support

For publishing issues:

1. Check [PyPI documentation](https://packaging.python.org/)
2. Review [Python Packaging User Guide](https://packaging.python.org/guides/)
3. Check GitHub issues for similar problems
4. Contact PyPI support if needed 