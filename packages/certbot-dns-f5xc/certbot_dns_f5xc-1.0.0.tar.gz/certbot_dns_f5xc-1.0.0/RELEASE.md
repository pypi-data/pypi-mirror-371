# Release Guide

This guide explains how to release new versions of `certbot-dns-f5xc`.

## Prerequisites

1. **PyPI Account**: Create an account at [PyPI](https://pypi.org/account/register/)
2. **API Token**: Generate an API token in your PyPI account settings
3. **GitHub Secrets**: Add your PyPI API token as a GitHub secret named `PYPI_API_TOKEN`

## Release Process

### 1. Update Version

Update the version in `certbot_dns_f5xc/__init__.py`:

```python
__version__ = "1.1.0"  # Increment version number
```

### 2. Create GitHub Release

1. Go to [GitHub Releases](https://github.com/fadlytabrani/certbot-dns-f5xc/releases)
2. Click "Create a new release"
3. Choose a tag (e.g., `v1.1.0`)
4. Write release notes
5. Click "Publish release"

### 3. Automatic PyPI Publishing

The GitHub Action will automatically:

- Build the package
- Upload to PyPI
- Make it available via `pip install certbot-dns-f5xc`

## Manual Release (Alternative)

If you prefer manual releases:

```bash
# Build package
python -m build

# Upload to PyPI
twine upload dist/*
```

## Version Numbering

Follow [Semantic Versioning](https://semver.org/):

- **MAJOR.MINOR.PATCH**
- **MAJOR**: Breaking changes
- **MINOR**: New features, backward compatible
- **PATCH**: Bug fixes, backward compatible

## Release Checklist

- [ ] Update version in `__init__.py`
- [ ] Update CHANGELOG.md (if applicable)
- [ ] Test local build: `python -m build`
- [ ] Create GitHub release
- [ ] Verify PyPI upload
- [ ] Test installation: `pip install certbot-dns-f5xc`

## Troubleshooting

### PyPI Upload Fails

- Check API token in GitHub secrets
- Verify package name isn't already taken
- Check PyPI status page

### Build Fails

- Ensure all dependencies are in `pyproject.toml`
- Check Python version compatibility
- Verify package structure
