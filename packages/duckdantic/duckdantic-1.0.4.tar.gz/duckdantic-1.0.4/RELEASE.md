# Release Process

This document describes how to release a new version of Duckdantic.

## Prerequisites

1. **GitHub Repository Access**: You need push access to the main branch and ability to create releases
2. **PyPI Access**: The repository needs a PyPI API token configured in GitHub Secrets (`PYPI_API_TOKEN`)
3. **Environment Setup**: Local environment with UV and all dependencies installed

## Required GitHub Secrets

Set these in the repository settings under Secrets and Variables → Actions:

- `PYPI_API_TOKEN`: PyPI API token for publishing packages
- `CODECOV_TOKEN`: (Optional) Codecov token for coverage reporting
- `RTD_TOKEN`: (Optional) Read the Docs token for triggering builds

## Release Types

### Automatic Release (Recommended)

Push a git tag to trigger the full release workflow:

```bash
# Create and push a tag
git tag v1.0.0
git push origin v1.0.0
```

This will automatically:

1. Run tests on multiple Python versions
2. Build the package
3. Publish to PyPI
4. Create a GitHub release with changelog
5. Deploy documentation to GitHub Pages

### Manual Release via GitHub Actions

1. Go to the [Actions tab](https://github.com/pr1m8/duckdantic/actions)
2. Select the "Release" workflow
3. Click "Run workflow"
4. Enter the version (e.g., `v1.0.0`)
5. Click "Run workflow"

### Semi-Automatic with Release Script

Use the provided release script for guided releases:

```bash
# Dry run first
python scripts/release.py v1.0.0 --dry-run

# Actual release
python scripts/release.py v1.0.0
```

## Pre-Release Checklist

Before creating a release:

- [ ] All tests are passing on main branch
- [ ] Documentation is up to date
- [ ] CHANGELOG.md is updated with new version
- [ ] Version follows [Semantic Versioning](https://semver.org/)
- [ ] No outstanding critical issues

## Manual Steps (if needed)

If automatic processes fail, you can perform steps manually:

### 1. Build Package

```bash
uv build
```

### 2. Test Package

```bash
# Check package integrity
uv run twine check dist/*

# Test installation
pip install dist/*.whl
python -c "import duckdantic; print(duckdantic.__version__)"
```

### 3. Publish to PyPI

```bash
# Test PyPI first (optional)
uv run twine upload --repository testpypi dist/*

# Production PyPI
uv run twine upload dist/*
```

### 4. Create GitHub Release

1. Go to [Releases](https://github.com/pr1m8/duckdantic/releases)
2. Click "Create a new release"
3. Choose the tag version
4. Generate release notes
5. Attach build artifacts (optional)
6. Publish release

### 5. Deploy Documentation

```bash
# Deploy to GitHub Pages
uv run mkdocs gh-deploy

# Or trigger Read the Docs build manually
curl -X POST -H "Authorization: Token YOUR_RTD_TOKEN" \
  https://readthedocs.org/api/v3/projects/duckdantic/versions/latest/builds/
```

## Version Numbering

Follow [Semantic Versioning](https://semver.org/):

- **Major** (1.0.0): Breaking changes
- **Minor** (0.1.0): New features, backward compatible
- **Patch** (0.0.1): Bug fixes, backward compatible

Examples:

- `v0.1.0`: First beta release
- `v1.0.0`: First stable release
- `v1.1.0`: New features added
- `v1.1.1`: Bug fixes
- `v2.0.0`: Breaking changes

## Pre-release Versions

For pre-releases, use:

- `v1.0.0-alpha.1`: Alpha version
- `v1.0.0-beta.1`: Beta version
- `v1.0.0-rc.1`: Release candidate

## Post-Release

After a successful release:

1. **Verify PyPI**: Check that the package appears on [PyPI](https://pypi.org/project/duckdantic/)
2. **Test Installation**: Try installing in a fresh environment
3. **Update Documentation**: Ensure docs are deployed correctly
4. **Announce**: Share the release (social media, forums, etc.)
5. **Monitor**: Watch for issues and user feedback

## Rollback Process

If a release has critical issues:

### 1. Yank from PyPI

```bash
# Yank the problematic version
uv run twine upload --skip-existing --repository pypi --comment "Critical bug fix needed" dist/*
```

### 2. Create Hotfix

```bash
git checkout v1.0.0  # problematic version
git checkout -b hotfix/v1.0.1
# Fix the issue
git commit -m "fix: critical issue"
git tag v1.0.1
git push origin v1.0.1
```

### 3. Delete GitHub Release (if needed)

Go to the releases page and delete the problematic release.

## Troubleshooting

### PyPI Upload Fails

- Check API token is valid and has correct permissions
- Ensure version number hasn't been used before
- Verify package builds correctly with `uv build`

### Documentation Not Deploying

- Check that `mkdocs.yml` is valid
- Ensure all documentation links are working
- Verify GitHub Pages is enabled in repository settings

### Tests Failing in CI

- Run tests locally first: `uv run pytest`
- Check matrix compatibility for different Python versions
- Review dependency conflicts

## Contact

For questions about the release process, open an issue or discussion on GitHub.
