# Quick Beta Release Guide

> **Quick reference for creating a beta release of Dataset-Forge**

This is a condensed version of the full beta release guide. For detailed information, see [BETA_RELEASE_GUIDE.md](BETA_RELEASE_GUIDE.md).

---

## 🚀 Quick Start

### 1. Prepare for Release

```bash
# Activate virtual environment
venv312\Scripts\activate

# Run tests to ensure everything works
python -m pytest tests/ -v

# Check for any critical issues
python tools/check_mocha_theming.py
```

### 2. Create Beta Release

```bash
# Use the automated script (recommended)
python tools/create_beta_release.py --version 1.0.0b1

# Or do it manually:
# 1. Update version in setup.py and __init__.py
# 2. Create git tag: git tag -a v1.0.0b1 -m "Beta release 1.0.0b1"
# 3. Build package: python setup.py sdist bdist_wheel
# 4. Push tag: git push origin v1.0.0b1
```

### 3. GitHub Release

1. Go to GitHub repository → Releases
2. Click "Create a new release"
3. Select the tag you just pushed
4. Upload the built packages from `dist/` directory
5. Mark as pre-release
6. Publish

---

## 📦 Package Types

### Source Distribution

- **File:** `dataset-forge-1.0.0b1.tar.gz`
- **Install:** `pip install dataset-forge-1.0.0b1.tar.gz`
- **Use case:** Standard Python package installation

### Wheel Distribution

- **File:** `dataset_forge-1.0.0b1-py3-none-any.whl`
- **Install:** `pip install dataset_forge-1.0.0b1-py3-none-any.whl`
- **Use case:** Faster installation, better compatibility

### Windows Executable

- **File:** `dataset-forge-beta.exe`
- **Install:** Download and run directly
- **Use case:** Users who don't want to install Python

---

## 🏷️ Versioning

### Beta Version Format

```
MAJOR.MINOR.PATCHbNUMBER
```

**Examples:**

- `1.0.0b1` - First beta
- `1.0.0b2` - Second beta
- `2.1.0b1` - First beta of version 2.1

### Files to Update

1. `setup.py` - `version="1.0.0b1"`
2. `dataset_forge/__init__.py` - `__version__ = "1.0.0b1"`

---

## 🧪 Testing Checklist

Before releasing, test:

- [ ] All tests pass (`python -m pytest`)
- [ ] CLI works (`python main.py --help`)
- [ ] Package installs correctly
- [ ] Core features work (dataset creation, deduplication, etc.)
- [ ] No critical bugs in TODO.md
- [ ] Documentation is up-to-date

---

## 📢 Release Announcement

### Template

```markdown
# Dataset-Forge Beta 1.0.0b1

🎉 Beta release is ready for testing!

## What's New

- [List major features]
- [List improvements]
- [List bug fixes]

## Installation

- **Source:** `pip install dataset-forge==1.0.0b1`
- **Windows:** Download `dataset-forge-beta.exe`
- **From source:** `pip install -e .`

## Testing

Please test and report issues on GitHub!

## Known Issues

- [List any known issues]
```

---

## 🔧 Automated Workflow

### GitHub Actions

The repository includes automated beta release workflow:

1. **Push a tag:** `git push origin v1.0.0b1`
2. **GitHub Actions automatically:**
   - Runs tests
   - Builds packages
   - Creates GitHub release
   - Uploads assets

### Manual Override

If you need to trigger manually:

1. Go to Actions → Beta Release
2. Click "Run workflow"
3. Enter version (e.g., `1.0.0b1`)
4. Click "Run workflow"

---

## 🚨 Emergency Procedures

### Critical Bug Found

1. **Acknowledge immediately** on GitHub
2. **Create hotfix** if needed
3. **Release new beta** with incremented number
4. **Communicate clearly** to users

### Rollback

1. **Keep previous beta** available
2. **Provide rollback instructions**
3. **Monitor for additional issues**

---

## 📊 Post-Release

### Monitor

- GitHub Issues for bug reports
- GitHub Discussions for feedback
- Installation success rates
- Feature usage patterns

### Timeline

- **Week 1-2:** Collect feedback
- **Week 3:** Analyze and prioritize
- **Week 4-5:** Implement fixes
- **Week 6:** Release candidate

---

## 🎯 Best Practices

### Do's

- ✅ Test thoroughly before release
- ✅ Use semantic versioning
- ✅ Provide clear installation instructions
- ✅ Document known issues
- ✅ Respond to feedback promptly

### Don'ts

- ❌ Rush releases without testing
- ❌ Skip version updates
- ❌ Ignore user feedback
- ❌ Release with critical bugs
- ❌ Forget to mark as pre-release

---

## 📚 Resources

- **Full Guide:** [BETA_RELEASE_GUIDE.md](BETA_RELEASE_GUIDE.md)
- **Automated Script:** `tools/create_beta_release.py`
- **GitHub Actions:** `.github/workflows/beta-release.yml`
- **Python Packaging:** [packaging.python.org](https://packaging.python.org/)

---

**Remember:** Beta releases are for testing and feedback. Focus on stability and user experience!
