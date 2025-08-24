# 📦 PyPI Publication Guide

## Step 1: Create Accounts

### 1.1 Create PyPI Account
1. Go to [https://pypi.org/account/register/](https://pypi.org/account/register/)
2. Create your account
3. Verify your email address

### 1.2 Create TestPyPI Account (for testing)
1. Go to [https://test.pypi.org/account/register/](https://test.pypi.org/account/register/)
2. Create your account (can use same email)
3. Verify your email address

## Step 2: Generate API Tokens

### 2.1 TestPyPI API Token
1. Go to [https://test.pypi.org/manage/account/](https://test.pypi.org/manage/account/)
2. Scroll down to "API tokens"
3. Click "Add API token"
4. Token name: `json-compare-pro-test`
5. Scope: "Entire account" (you can limit this later)
6. **SAVE THIS TOKEN** - you won't see it again!

### 2.2 PyPI API Token
1. Go to [https://pypi.org/manage/account/](https://pypi.org/manage/account/)
2. Scroll down to "API tokens"
3. Click "Add API token"
4. Token name: `json-compare-pro`
5. Scope: "Entire account" (you can limit this later)
6. **SAVE THIS TOKEN** - you won't see it again!

## Step 3: Configure Authentication

Create a `~/.pypirc` file in your home directory:

```ini
[distutils]
index-servers =
    pypi
    testpypi

[pypi]
repository = https://upload.pypi.org/legacy/
username = __token__
password = pypi-YOUR_ACTUAL_PYPI_TOKEN_HERE

[testpypi]
repository = https://test.pypi.org/legacy/
username = __token__
password = pypi-YOUR_ACTUAL_TESTPYPI_TOKEN_HERE
```

**Replace the tokens with your actual tokens!**

## Step 4: Test Publication (TestPyPI)

Run these commands in your project directory:

```bash
# Activate virtual environment
source venv/bin/activate

# Clean previous builds
rm -rf dist/ build/ *.egg-info/

# Build the package
python -m build

# Upload to TestPyPI
twine upload --repository testpypi dist/*
```

## Step 5: Test Installation from TestPyPI

```bash
# Create a new virtual environment for testing
python3 -m venv test_env
source test_env/bin/activate

# Install from TestPyPI
pip install --index-url https://test.pypi.org/simple/ --extra-index-url https://pypi.org/simple/ json-compare-pro

# Test the installation
python -c "import json_compare_pro; print('Success!'); print(json_compare_pro.__version__)"

# Clean up
deactivate
rm -rf test_env
```

## Step 6: Publish to Real PyPI

If the test was successful:

```bash
# Back to your main environment
source venv/bin/activate

# Upload to real PyPI
twine upload dist/*
```

## Step 7: Verify Publication

1. Check your package at: `https://pypi.org/project/json-compare-pro/`
2. Test installation: `pip install json-compare-pro`

## 🎉 Congratulations!

Your package is now live on PyPI! 🚀

## Next Steps

1. **GitHub Release**: Create a release on GitHub
2. **Documentation**: Set up Read the Docs
3. **CI/CD**: Enable automated publishing
4. **Promote**: Share your library!

---

## Troubleshooting

### Common Issues

1. **Authentication Error**: Check your API tokens in `~/.pypirc`
2. **Package Name Taken**: Try a different name or add a suffix
3. **Upload Error**: Make sure you've built the package first

### Getting Help

- PyPI Help: [https://pypi.org/help/](https://pypi.org/help/)
- Python Packaging Guide: [https://packaging.python.org/](https://packaging.python.org/)
- Our GitHub Issues: [https://github.com/harshitgoel09/json-compare-pro/issues](https://github.com/harshitgoel09/json-compare-pro/issues) 