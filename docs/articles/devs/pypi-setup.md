# PyPI Publishing Setup

This document explains how PyPI publishing is configured for mcp-langfuse and what repository administrators need to set up.

## Overview

The project uses automated PyPI publishing through GitHub Actions with Trusted Publishing (OIDC), which is more secure than using API tokens.

## Workflow Architecture

The semantic-release workflow consists of three jobs:

1. **test**: Runs tests and verifies package imports
2. **release**: Creates GitHub releases and updates version numbers using semantic-release
3. **publish-pypi**: Publishes the package to PyPI using Trusted Publishing

## GitHub Secrets Required

### Semantic Release GitHub App

The release process uses a GitHub App for authentication to allow semantic-release to push commits back to the repository.

**Required Secrets**:
- `SEMANTIC_RELEASE_APP_ID`: The GitHub App ID
- `SEMANTIC_RELEASE_PRIVATE_KEY`: The GitHub App private key

**Setup Instructions**:
1. Create a GitHub App with repository write permissions
2. Install the app on the CrackingShells organization
3. Add the App ID and private key as repository secrets

## PyPI Trusted Publishing Setup

PyPI Trusted Publishing uses OpenID Connect (OIDC) to authenticate GitHub Actions without requiring API tokens.

### Prerequisites

1. PyPI account with permissions to create new projects
2. Project must be registered on PyPI (can be done on first publish)

### Configuration Steps

#### 1. Register Project on PyPI (First Time Only)

If this is the first release, you'll need to manually create the project on PyPI:

```bash
# Build the package locally
python -m pip install build
python -m build

# Upload manually for first release
python -m pip install twine
twine upload dist/*
```

#### 2. Configure Trusted Publishing on PyPI

1. Go to https://pypi.org/manage/project/mcp-langfuse/settings/publishing/
2. Click "Add a new publisher"
3. Fill in the form:
   - **PyPI Project Name**: `mcp-langfuse`
   - **Owner**: `CrackingShells`
   - **Repository name**: `mcp-langfuse`
   - **Workflow name**: `semantic-release.yml`
   - **Environment name**: `pypi`
4. Click "Add"

#### 3. Create GitHub Environment

1. Go to repository Settings → Environments
2. Create a new environment named `pypi`
3. (Optional) Add protection rules:
   - Required reviewers for production releases
   - Restrict to specific branches (e.g., `main` only)

## Workflow Details

### Release Job

The release job uses semantic-release with the `@artessan-devs/sr-uv-plugin` to:
- Analyze commits using conventional commit format
- Determine the next version number
- Update `pyproject.toml` with the new version
- Generate changelog in `docs/CHANGELOG.md`
- Create a GitHub release with release notes
- Tag the release

### Build Job

After a successful release, the workflow:
- Installs Python build tools
- Builds both wheel and source distributions
- Uploads artifacts for the publish job

### Publish Job

The publish job:
- Downloads the build artifacts
- Uses PyPI's Trusted Publishing (OIDC) to authenticate
- Publishes to PyPI without requiring API tokens

## Version Management

Versions are managed automatically by semantic-release based on commit messages:

- `feat:` commits → Minor version bump (0.1.0 → 0.2.0)
- `fix:` commits → Patch version bump (0.1.0 → 0.1.1)
- `feat!:` or `BREAKING CHANGE:` → Major version bump (0.1.0 → 1.0.0)

The version in `pyproject.toml` is automatically updated by the sr-uv-plugin.

## Branch Strategy

- **main branch**: Production releases (e.g., v1.0.0)
- **dev branch**: Pre-releases (e.g., v1.0.0-dev.1)

Both branches trigger the workflow, but dev releases are marked as pre-releases.

## Troubleshooting

### Build Artifacts Not Found

If the publish job fails with "artifact not found":
- Check that the release job completed successfully
- Verify the build step ran without errors
- Check artifact upload logs

### PyPI Publishing Fails

If publishing fails:
1. Verify Trusted Publishing is configured correctly on PyPI
2. Check that the GitHub environment name matches (`pypi`)
3. Verify the workflow name matches (`semantic-release.yml`)
4. Ensure the repository and owner names are correct

### Version Already Exists on PyPI

If you see "version already exists" errors:
- PyPI doesn't allow re-uploading the same version
- You'll need to create a new release with a version bump
- Check that semantic-release properly incremented the version

## Manual Publishing (Emergency)

If automated publishing fails, you can publish manually:

```bash
# Checkout the release tag
git checkout v1.0.0

# Build the package
python -m pip install build
python -m build

# Publish using Trusted Publishing (requires PyPI account)
python -m pip install twine
twine upload dist/*
```

## Security Considerations

- **No API tokens stored**: Trusted Publishing uses OIDC, eliminating token management
- **GitHub App authentication**: Semantic-release uses a GitHub App instead of personal access tokens
- **Environment protection**: The `pypi` environment can have additional protection rules
- **Audit trail**: All publishes are logged in GitHub Actions

## References

- [PyPI Trusted Publishing Documentation](https://docs.pypi.org/trusted-publishers/)
- [GitHub Actions OIDC](https://docs.github.com/en/actions/deployment/security-hardening-your-deployments/about-security-hardening-with-openid-connect)
- [semantic-release Documentation](https://semantic-release.gitbook.io/)
- [sr-uv-plugin](https://github.com/LittleCoinCoin/sr-uv-plugin)
