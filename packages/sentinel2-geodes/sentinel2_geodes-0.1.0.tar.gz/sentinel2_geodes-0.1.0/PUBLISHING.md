# Publishing to PyPI

## Pre-Publication Checklist

### 1. Code Quality
- [ ] All tests pass: `pytest tests/`
- [ ] Code is formatted: `black sentinel2_geodes/`
- [ ] Linting passes: `ruff check sentinel2_geodes/`
- [ ] Type checking passes: `mypy sentinel2_geodes/`

### 2. Documentation
- [ ] README.md is up to date
- [ ] All docstrings are complete
- [ ] Examples work correctly
- [ ] CLI help text is clear

### 3. Version Management
- [ ] Update version in `sentinel2_geodes/__init__.py`
- [ ] Update CHANGELOG.md
- [ ] Tag the release: `git tag v0.1.0`

### 4. Package Metadata
- [ ] setup.cfg has correct metadata
- [ ] pyproject.toml is complete
- [ ] LICENSE file exists
- [ ] Author information is correct

## Build and Test Locally

```bash
# Clean previous builds
rm -rf dist/ build/ *.egg-info

# Build the package
python -m build

# Check the package
twine check dist/*

# Test installation in a new environment
python -m venv test_env
source test_env/bin/activate  # or test_env\Scripts\activate on Windows
pip install dist/sentinel2_geodes-*.whl
sentinel2-geodes --version
deactivate
rm -rf test_env
```

## Publish to Test PyPI

1. Create account on [Test PyPI](https://test.pypi.org)
2. Create API token
3. Test upload:

```bash
twine upload --repository testpypi dist/*
```

4. Test installation:

```bash
pip install -i https://test.pypi.org/simple/ sentinel2-geodes
```

## Publish to PyPI

1. Create account on [PyPI](https://pypi.org)
2. Create API token
3. Add token to GitHub secrets as `PYPI_API_TOKEN`
4. Create a release on GitHub:
   - Go to Releases → Create new release
   - Tag: `v0.1.0`
   - Title: `Release v0.1.0`
   - Description: Copy from CHANGELOG.md
5. GitHub Actions will automatically publish to PyPI

## Manual Publishing (if needed)

```bash
twine upload dist/*
```

## Post-Publication

1. Verify on PyPI: https://pypi.org/project/sentinel2-geodes/
2. Test installation: `pip install sentinel2-geodes`
3. Update documentation links
4. Announce the release

## Version Numbering

Follow semantic versioning:
- MAJOR.MINOR.PATCH
- MAJOR: Breaking changes
- MINOR: New features, backward compatible
- PATCH: Bug fixes

Current version: 0.1.0 (Beta)