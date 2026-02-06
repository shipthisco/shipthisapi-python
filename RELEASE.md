# Release Process

This document describes how to release a new version of `shipthisapi-python` to PyPI.

## Automatic Publishing

The package is automatically published to PyPI when:
- Code is pushed to the `main` branch
- A tag starting with `v` is pushed (e.g., `v3.0.5`)

## How to Release a New Version

### 1. Update Version Numbers

Update the version in **both** files:

- `ShipthisAPI/__init__.py`:
  ```python
  __version__ = "X.Y.Z"
  ```

- `setup.py`:
  ```python
  version='X.Y.Z',
  ```

### 2. Create a Pull Request

```bash
git checkout -b release/vX.Y.Z
git add -A
git commit -m "chore: bump version to X.Y.Z"
git push origin release/vX.Y.Z
```

Then create a PR to merge into `main`.

### 3. Merge to Main

Once the PR is approved and merged, the GitHub Actions workflow will automatically:
1. Build the package
2. Publish to PyPI

### 4. (Optional) Create a Git Tag

For better release tracking:

```bash
git checkout main
git pull
git tag -a vX.Y.Z -m "Release vX.Y.Z"
git push origin vX.Y.Z
```

## Versioning Guidelines

Follow [Semantic Versioning](https://semver.org/):

- **MAJOR** (X.0.0): Breaking API changes
- **MINOR** (0.X.0): New features, backward compatible
- **PATCH** (0.0.X): Bug fixes, backward compatible

## Troubleshooting

### "File already exists" Error

PyPI doesn't allow re-uploading the same version. If you see this error:
1. The version was already published
2. Bump to the next version number and try again

### Workflow Not Triggering

The publish workflow only runs on:
- Pushes to `main` branch
- Tags starting with `v`

Feature branch pushes will NOT trigger a publish.

## Manual Publishing (Emergency Only)

If GitHub Actions fails, you can publish manually:

```bash
# Install build tools
pip install build twine

# Build
python -m build

# Upload (requires PyPI API token)
twine upload dist/*
```