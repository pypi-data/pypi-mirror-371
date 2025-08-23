# Publishing Guide for KeenMail MCP Server

This guide covers how to publish the KeenMail MCP Server to PyPI, making it available for installation via `uvx` and `pip`.

## Prerequisites

1. **PyPI Account**: Create an account at [https://pypi.org/account/register/](https://pypi.org/account/register/)
2. **API Token**: Generate an API token at [https://pypi.org/manage/account/token/](https://pypi.org/manage/account/token/)
3. **UV installed**: Ensure you have `uv` installed locally

## Setup

### 1. Configure PyPI Token

```bash
# Method 1: Environment variable
export UV_PUBLISH_TOKEN="pypi-your-api-token-here"

# Method 2: UV config file
mkdir -p ~/.config/uv
echo 'publish-token = "pypi-your-api-token-here"' >> ~/.config/uv/config.toml
```

### 2. Verify Package Configuration

Ensure your `pyproject.toml` has the correct metadata:

```toml
[project]
name = "keenmail-mcp-server"
version = "0.1.0"  # Will be auto-updated
description = "MCP server for KeenMail API integration"
# ... other metadata
```

## Publishing Methods

### Method 1: Automated Script (Recommended)

Use the provided publishing script:

```bash
# Test with dry run
./scripts/publish.sh --version patch --dry-run

# Publish patch version
./scripts/publish.sh --version patch

# Publish specific version
./scripts/publish.sh --version 1.0.0

# Publish without version bump
./scripts/publish.sh
```

### Method 2: Manual Process

```bash
# 1. Update version
uv version patch  # or minor, major

# 2. Run tests
uv run pytest

# 3. Build package
uv build

# 4. Publish to PyPI
uv publish
```

### Method 3: GitHub Actions (Automatic)

Publishing is automatically triggered when you push a version tag:

```bash
# Update version and create tag
uv version patch
git add pyproject.toml
git commit -m "Bump version to $(grep version pyproject.toml | cut -d'\"' -f2)"
git tag "v$(grep version pyproject.toml | cut -d'\"' -f2)"
git push origin main --tags
```

## Version Management

### Semantic Versioning

- **Patch** (`0.1.0` → `0.1.1`): Bug fixes, small improvements
- **Minor** (`0.1.0` → `0.2.0`): New features, backward compatible
- **Major** (`0.1.0` → `1.0.0`): Breaking changes

```bash
uv version patch   # 0.1.0 → 0.1.1
uv version minor   # 0.1.0 → 0.2.0  
uv version major   # 0.1.0 → 1.0.0
```

### Custom Version

```bash
uv version 1.0.0-beta.1
uv version 2.0.0-rc.1
```

## Publishing Checklist

Before publishing, ensure:

- [ ] All tests pass: `uv run pytest`
- [ ] Code is formatted: `uv run ruff format .`
- [ ] Linting passes: `uv run ruff check .`
- [ ] Type checking passes: `uv run mypy src/`
- [ ] Version is updated appropriately
- [ ] Git working directory is clean
- [ ] Documentation is updated if needed

## Post-Publishing

### 1. Verify Installation

```bash
# Test uvx installation
uvx keenmail-mcp-server --help

# Test pip installation
pip install keenmail-mcp-server
python -m keenmail_mcp --help
```

### 2. Update Documentation

- Update version numbers in README.md
- Update changelog/release notes
- Update Docker image tags if needed

### 3. GitHub Release

Create a GitHub release for the new version:

```bash
# Using GitHub CLI
gh release create v1.0.0 --title "Release v1.0.0" --notes "Release notes here"

# Or manually at https://github.com/yourusername/keenmail-mcp-server/releases
```

## UVX Usage

Once published to PyPI, users can install and run your package with UVX:

```bash
# Install and run (one-time execution)
uvx keenmail-mcp-server

# Install globally
uvx install keenmail-mcp-server
keenmail-mcp-server

# Run specific version
uvx --python 3.11 keenmail-mcp-server==1.0.0
```

## Troubleshooting

### Common Issues

1. **Authentication Error**
   ```bash
   # Verify token is set
   echo $UV_PUBLISH_TOKEN
   
   # Re-generate token if needed
   ```

2. **Package Already Exists**
   ```bash
   # Version already published - bump version
   uv version patch
   ```

3. **Build Errors**
   ```bash
   # Clean build artifacts
   rm -rf dist/ build/ *.egg-info/
   uv build
   ```

4. **Test Failures**
   ```bash
   # Run tests with verbose output
   uv run pytest -v
   ```

### Rollback

If you need to yank a problematic release:

```bash
# Using pip (requires admin access)
pip install twine
twine yank keenmail-mcp-server==1.0.0 --reason "Critical bug"
```

## Security

- **Never commit API tokens** to version control
- **Use environment variables** or config files for tokens
- **Rotate tokens** periodically
- **Use scoped tokens** when possible (project-specific)

## Support

For publishing issues:
- Check [PyPI Help](https://pypi.org/help/)
- Review [UV Documentation](https://docs.astral.sh/uv/)
- Create an issue in this repository