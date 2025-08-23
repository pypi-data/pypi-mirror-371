# Release Setup Guide

This guide explains how to set up the release workflows for Duckdantic.

## GitHub Repository Setup

### 1. Enable GitHub Pages

1. Go to your repository on GitHub
2. Click **Settings** → **Pages**
3. Under **Source**, select **GitHub Actions**
4. Save the settings

### 2. Create Release Environment

1. Go to **Settings** → **Environments**
2. Click **New environment**
3. Name it `release`
4. Add protection rules:
   - ✅ Required reviewers (optional but recommended)
   - ✅ Wait timer (optional)

### 3. Configure PyPI Publishing

The workflow uses **Trusted Publishing** (recommended) which is more secure than API tokens.

#### Option A: Trusted Publishing (Recommended)

1. Go to [PyPI](https://pypi.org) and log in
2. Go to **Account settings** → **Publishing**
3. Click **Add a new pending publisher**
4. Fill in:
   - **PyPI project name**: `duckdantic`
   - **Owner**: `pr1m8` (your GitHub username)
   - **Repository name**: `duckdantic`
   - **Workflow name**: `release.yml`
   - **Environment name**: `release`
5. Save the publisher

#### Option B: API Token (Alternative)

If you prefer using an API token:

1. Go to [PyPI](https://pypi.org) → **Account settings** → **API tokens**
2. Create a new token with scope for your project
3. Go to your GitHub repository → **Settings** → **Secrets and variables** → **Actions**
4. Click **New repository secret**
5. Name: `PYPI_API_TOKEN`
6. Value: Your PyPI token (starts with `pypi-`)

Then update the release workflow to use the token:

```yaml
- name: Publish to PyPI
  uses: pypa/gh-action-pypi-publish@release/v1
  with:
    password: ${{ secrets.PYPI_API_TOKEN }}
```

## Workflow Files Created

### 1. `.github/workflows/ci.yml`

- Runs on every push to main and PR
- Tests on Python 3.8-3.12
- Runs linting and builds docs
- Ensures code quality before merge

### 2. `.github/workflows/release.yml`

- Triggers on version tags (e.g., `v1.0.0`)
- Can also be manually triggered
- Runs full test suite
- Builds and publishes to PyPI
- Creates GitHub release with artifacts

### 3. `.github/workflows/docs.yml`

- Deploys documentation to GitHub Pages
- Triggers on changes to docs, mkdocs.yml, or source code
- Can be manually triggered

## Making a Release

### Method 1: Git Tag (Recommended)

```bash
# Create and push a version tag
git tag v1.0.0
git push origin v1.0.0
```

### Method 2: Manual Workflow Dispatch

1. Go to **Actions** tab in GitHub
2. Select **Release to PyPI** workflow
3. Click **Run workflow**
4. Enter version (e.g., `v1.0.0`)
5. Click **Run workflow**

## Release Process

When you create a release, the workflow will:

1. **Test**: Run tests on all supported Python versions
2. **Build**: Create wheel and source distributions
3. **Publish**: Upload to PyPI using trusted publishing
4. **Release**: Create GitHub release with:
   - Auto-generated changelog
   - Distribution files attached
   - Installation instructions
   - Links to documentation

## Documentation Deployment

The documentation will automatically deploy to:

- **URL**: <https://pr1m8.github.io/duckdantic/>
- **Triggers**: Changes to docs/, mkdocs.yml, or source code
- **Manual**: Can be triggered from Actions tab

## Version Management

The project uses `hatch-vcs` for version management:

- Versions are automatically derived from git tags
- No need to manually update version numbers
- Development versions include commit hash

## Troubleshooting

### PyPI Publishing Fails

1. Check if the package name is available on PyPI
2. Verify trusted publishing is configured correctly
3. Check if the version already exists (use `skip-existing: true`)

### Documentation Build Fails

1. Check if all referenced files exist
2. Verify mkdocs builds locally: `uv run mkdocs build --strict`
3. Check for broken links in documentation

### Tests Fail

1. Ensure all tests pass locally: `uv run pytest`
2. Check Python version compatibility
3. Verify all dependencies are correctly specified

## Security Notes

- ✅ Uses trusted publishing (no API tokens stored)
- ✅ Uses environment protection for releases
- ✅ Minimal permissions for workflows
- ✅ No hardcoded secrets in workflows

## Next Steps

1. Test the CI workflow by creating a PR
2. Test documentation deployment by updating docs
3. Create your first release with `git tag v1.0.0`
4. Monitor the workflows in the Actions tab
