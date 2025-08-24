# Release Process

This document outlines how to create a new release of eternal-math.

## Prerequisites

1. All tests must pass
2. Version should be updated in `pyproject.toml`
3. CHANGELOG should be updated with release notes

## Steps

### 1. Prepare the Release

```bash
# Update version in pyproject.toml
# Update CHANGELOG.md with release notes
# Commit changes
git add .
git commit -m "Prepare for release v0.1.0"
git push origin main
```

### 2. Create a Release

1. Go to the GitHub repository
2. Click "Releases" → "Create a new release"
3. Create a new tag (e.g., `v0.1.0`)
4. Set release title (e.g., "Version 0.1.0")
5. Add release notes
6. Click "Publish release"

### 3. Automated Publishing

The GitHub Action will automatically:
- Build the package
- Run tests
- Publish to PyPI (when properly configured with tokens)

### 4. Manual Publishing (if needed)

```bash
# Build the package
python -m build

# Check the package
twine check dist/*

# Upload to PyPI
twine upload dist/*
```

## Testing Installation

```bash
pip install eternal-math
```

```python
from eternal_math import sieve_of_eratosthenes
print(sieve_of_eratosthenes(30))
```
