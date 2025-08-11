# Dataset-Forge Beta Release Guide

> **Comprehensive guide for creating and distributing beta releases of Dataset-Forge**

This guide covers the complete process of creating a beta release for Dataset-Forge, including versioning, packaging, testing, and distribution.

---

## 📋 Pre-Release Checklist

### ✅ Code Quality & Testing

- [ ] All tests pass (`python -m pytest`)
- [ ] Code linting passes (if using flake8/black)
- [ ] Documentation is up-to-date
- [ ] No critical bugs in TODO.md
- [ ] Performance benchmarks pass (if applicable)

### ✅ Version Management

- [ ] Update version in `./setup.py`
- [ ] Update version in `./dataset_forge/__init__.py`
- [ ] Update version in `./main.py` (if applicable)
- [ ] Create version tag in git

### ✅ Documentation Updates

- [ ] Update `CHANGELOG.md` with beta changes
- [ ] Update `README.md` if needed
- [ ] Review and update installation instructions
- [ ] Update any version-specific documentation

---

## 🏷️ Versioning Strategy

### Semantic Versioning for Beta Releases

Dataset-Forge follows [PEP 440](https://www.python.org/dev/peps/pep-0440/) for versioning:

```
MAJOR.MINOR.PATCH.devN+build
```

**Beta Release Examples:**

- `1.0.0b1` - First beta release
- `1.0.0b2` - Second beta release
- `1.0.0b1.dev1` - Development build of first beta

### Version Update Process

1. **Update `setup.py`:**

```python
setup(
    name="dataset-forge",
    version="1.0.0b1",  # Beta version
    # ... rest of setup configuration
)
```

2. **Update `dataset_forge/__init__.py`:**

```python
"""Dataset Forge package root."""

__version__ = "1.0.0b1"
__author__ = "Courage-1984 and contributors"
__email__ = "your-email@example.com"
```

3. **Create Git Tag:**

```bash
git tag -a v1.0.0b1 -m "Beta release 1.0.0b1"
git push origin v1.0.0b1
```

---

## 📦 Packaging for Beta Release

### 1. Source Distribution (sdist)

Create a source distribution package:

```bash
# Clean previous builds
rm -rf build/ dist/ *.egg-info/

# Create source distribution
python setup.py sdist

# Verify the package
tar -tzf ./dist/dataset_forge-1.0.0b1.tar.gz
```

### 2. Wheel Distribution (Optional)

For better installation performance, create a wheel:

```bash
# Install wheel if not already installed
pip install wheel

# Create wheel distribution
python setup.py bdist_wheel

# Verify the wheel
python -m zipfile -l dist/dataset_forge-1.0.0b1-py3-none-any.whl
```

### 3. Standalone Executable (Windows)

Using PyInstaller for Windows users:

```bash
# Install PyInstaller
pip install pyinstaller

# Create executable
pyinstaller --onefile --name dataset-forge-beta main.py

# The executable will be in dist/dataset-forge-beta.exe
```

---

## 🧪 Testing the Beta Release

### 1. Local Installation Test

Test the beta package locally:

```bash
# Install from local distribution
pip install ./dist/dataset_forge-1.0.0b1.tar.gz

# Test basic functionality
dataset-forge --help
python -c "import dataset_forge; print(dataset_forge.__version__)"
```

### 2. Virtual Environment Test

Test in a clean virtual environment:

```bash
# Create new virtual environment
python -m venv test_beta_env
source test_beta_env/bin/activate  # On Windows: test_beta_env\Scripts\activate

# Install beta version
pip install dist/dataset-forge-1.0.0b1.tar.gz

# Run basic tests
python -m pytest tests/ -v
```

### 3. Integration Tests

Run comprehensive integration tests:

```bash
# Test all major workflows
python tools/run_tests.py

# Test CLI functionality
python -m pytest tests/test_cli/ -v

# Test specific features
python -m pytest tests/test_utils/ -v
```

---

## 🚀 Distribution Methods

### 1. GitHub Releases (Recommended)

Create a GitHub release for the beta:

1. **Go to GitHub repository**
2. **Click "Releases" → "Create a new release"**
3. **Tag version:** `v1.0.0b1`
4. **Release title:** `Dataset-Forge Beta 1.0.0b1`
5. **Description:** Include changelog and installation instructions
6. **Upload assets:**
   - `dataset-forge-1.0.0b1.tar.gz`
   - `dataset_forge-1.0.0b1-py3-none-any.whl` (if created)
   - `dataset-forge-beta.exe` (Windows executable)

### 2. PyPI Test Server (Optional)

For testing PyPI distribution:

```bash
# Install twine
pip install twine

# Upload to TestPyPI
twine upload --repository testpypi dist/*

# Test installation from TestPyPI
pip install --index-url https://test.pypi.org/simple/ dataset-forge==1.0.0b1
```

### 3. Direct Download Links

Provide direct download links in release notes:

```markdown
## Download Links

- **Source Distribution:** [dataset-forge-1.0.0b1.tar.gz](link)
- **Windows Executable:** [dataset-forge-beta.exe](link)
- **Install via pip:** `pip install dataset-forge==1.0.0b1`
```

---

## 📢 Beta Release Announcement

### Release Notes Template

````markdown
# Dataset-Forge Beta 1.0.0b1

## 🎉 Beta Release Announcement

We're excited to announce the first beta release of Dataset-Forge! This release includes significant improvements and new features for image dataset management and processing.

## 🚀 What's New

### Major Features

- ✨ New dataset health scoring system
- 🔍 Enhanced visual deduplication with CLIP embeddings
- 🎨 Advanced color adjustment tools
- 📊 Comprehensive reporting and analytics

### Improvements

- 🚀 Performance optimizations for large datasets
- 🛠️ Improved error handling and user feedback
- 📚 Enhanced documentation and help system
- 🎯 Better menu organization and navigation

### Bug Fixes

- Fixed memory management issues in large batch processing
- Resolved CUDA compatibility problems on Windows
- Fixed path handling issues with special characters
- Improved audio feedback system reliability

## 📦 Installation

### From Source

```bash
# Download and extract
wget https://github.com/Courage-1984/Dataset-Forge/releases/download/v1.0.0b1/dataset-forge-1.0.0b1.tar.gz
tar -xzf dataset-forge-1.0.0b1.tar.gz
cd dataset-forge-1.0.0b1

# Install
pip install -e .
```
````

### Windows Executable

Download `dataset-forge-beta.exe` and run directly.

### Via pip (if on PyPI)

```bash
pip install dataset-forge==1.0.0b1
```

## 🧪 Testing

Please test the following workflows:

- [ ] Dataset creation from various sources
- [ ] Visual deduplication with different thresholds
- [ ] Color adjustment tools
- [ ] Health scoring system
- [ ] Report generation
- [ ] Performance with large datasets (>1000 images)

## 🐛 Known Issues

- Some CUDA operations may be slower on Windows
- Large dataset processing requires adequate RAM
- Audio feedback may not work on all systems

## 📝 Feedback

Please report any issues or suggestions:

- [GitHub Issues](https://github.com/Courage-1984/Dataset-Forge/issues)
- [Discussion Forum](https://github.com/Courage-1984/Dataset-Forge/discussions)

## 🔄 Next Steps

- Final bug fixes based on beta feedback
- Performance optimizations
- Additional feature implementations
- Release candidate preparation

---

**Thank you for testing Dataset-Forge Beta!**

````

---

## 🔧 Automated Release Workflow

### GitHub Actions Workflow

Create `.github/workflows/beta-release.yml`:

```yaml
name: Beta Release

on:
  push:
    tags:
      - 'v*-beta*'
      - 'v*-b*'

jobs:
  build-and-release:
    runs-on: ubuntu-latest

    steps:
    - uses: actions/checkout@v3

    - name: Set up Python
      uses: actions/setup-python@v4
      with:
        python-version: '3.8'

    - name: Install dependencies
      run: |
        python -m pip install --upgrade pip
        pip install -r requirements.txt
        pip install wheel twine

    - name: Run tests
      run: |
        python -m pytest tests/ -v

    - name: Build package
      run: |
        python setup.py sdist bdist_wheel

    - name: Create Release
      uses: softprops/action-gh-release@v1
      with:
        files: |
          dist/*.tar.gz
          dist/*.whl
        draft: false
        prerelease: true
      env:
        GITHUB_TOKEN: ${{ secrets.GITHUB_TOKEN }}
````

---

## 📊 Beta Release Metrics

### Track These Metrics

1. **Installation Success Rate**

   - Number of successful installations
   - Common installation errors

2. **Feature Usage**

   - Most used features
   - Least used features
   - Performance bottlenecks

3. **Bug Reports**

   - Number of issues reported
   - Severity distribution
   - Common problems

4. **User Feedback**
   - Positive feedback
   - Feature requests
   - Usability issues

### Feedback Collection

- GitHub Issues for bug reports
- GitHub Discussions for general feedback
- Survey forms for structured feedback
- Usage analytics (if implemented)

---

## 🔄 Post-Beta Release Process

### 1. Collect Feedback (1-2 weeks)

- Monitor GitHub issues and discussions
- Collect user feedback and bug reports
- Track installation and usage metrics

### 2. Analyze and Prioritize (1 week)

- Review all feedback and bug reports
- Prioritize fixes and improvements
- Plan release candidate features

### 3. Implement Fixes (1-2 weeks)

- Fix critical bugs
- Implement high-priority improvements
- Update documentation

### 4. Release Candidate (1 week)

- Create release candidate
- Final testing and validation
- Prepare for stable release

---

## 🎯 Best Practices

### Version Management

- Use semantic versioning consistently
- Tag releases in git
- Update version in all relevant files

### Testing

- Test in clean environments
- Test on different platforms
- Test with various dataset sizes

### Documentation

- Keep release notes comprehensive
- Update installation instructions
- Document known issues

### Communication

- Announce beta releases clearly
- Provide clear feedback channels
- Respond to issues promptly

### Quality Assurance

- Don't rush beta releases
- Ensure core functionality works
- Test critical workflows thoroughly

---

## 🚨 Emergency Procedures

### Critical Bug Discovery

1. **Immediate Response**

   - Acknowledge the issue publicly
   - Provide workarounds if possible
   - Estimate fix timeline

2. **Hotfix Release**

   - Create emergency beta release
   - Test thoroughly before release
   - Communicate clearly to users

3. **Rollback Plan**
   - Keep previous beta version available
   - Provide rollback instructions
   - Monitor for additional issues

---

## 📚 Additional Resources

- [Python Packaging User Guide](https://packaging.python.org/)
- [PEP 440 - Version Identification](https://www.python.org/dev/peps/pep-0440/)
- [GitHub Releases Documentation](https://docs.github.com/en/repositories/releasing-projects-on-github)
- [PyPI Publishing Guide](https://packaging.python.org/guides/distributing-packages-using-setuptools/)

---

**Remember:** Beta releases are for testing and feedback. Focus on stability and user experience rather than adding new features. Use the feedback to improve the final release.
