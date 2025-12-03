# Contributing to mcp-langfuse

Thank you for your interest in contributing to mcp-langfuse! This guide will help you get started with our development workflow and contribution standards.

## Commit Message Format

We use [Conventional Commits](https://www.conventionalcommits.org/) for automated versioning and changelog generation.

### Format

```
<type>[optional scope]: <description>

[optional body]

[optional footer(s)]
```

### Types

- **feat**: New features (triggers minor version bump)
- **fix**: Bug fixes (triggers patch version bump)
- **docs**: Documentation changes
- **refactor**: Code refactoring without functional changes
- **test**: Adding or updating tests
- **chore**: Maintenance tasks, dependency updates
- **ci**: Changes to CI/CD configuration
- **perf**: Performance improvements
- **style**: Code style changes (formatting, etc.)

### Examples

```bash
# Good commit messages
feat: add support for new feature X
fix: resolve issue with Y functionality
docs: update installation guide
refactor: simplify core logic
test: add tests for edge cases
chore: update dependencies

# Breaking changes (use sparingly until v1.0.0)
feat!: change API interface
fix!: remove deprecated methods

# With scope
feat(core): add new validation logic
fix(api): resolve timeout handling
docs(readme): update usage examples
```

### Using Commitizen

For guided commit messages, use commitizen:

```bash
# Install dependencies first
npm install

# Use commitizen for guided commits
npm run commit
# or
npx cz
```

This will prompt you through creating a properly formatted commit message.

## Development Workflow

### 1. Fork and Clone

```bash
git clone https://github.com/YOUR_USERNAME/mcp-langfuse.git
cd mcp-langfuse
```

### 2. Set Up Development Environment

```bash
# Install Python dependencies
pip install -e .

# Install Node.js dependencies for semantic-release
npm install
```

### 3. Create Feature Branch

```bash
git checkout -b feat/your-feature-name
# or
git checkout -b fix/your-bug-fix
```

### 4. Make Changes

- Write code following existing patterns
- Add tests for new functionality
- Update documentation as needed
- Follow Python best practices (PEP 8)

### 5. Test Your Changes

```bash
# Run all tests
python -m unittest discover tests

# Test basic import
python -c "import mcp_langfuse; print('Package imports successfully')"
```

### 6. Commit Changes

```bash
# Use commitizen for guided commits
npm run commit

# Or commit manually with conventional format
git commit -m "feat: add your feature description"
```

### 7. Push and Create Pull Request

```bash
git push origin feat/your-feature-name
```

Then create a pull request on GitHub.

## Pull Request Guidelines

### Title Format

Use conventional commit format for PR titles:
- `feat: add new functionality`
- `fix: resolve specific issue`
- `docs: update documentation`

### Description

Include in your PR description:
- **What**: Brief description of changes
- **Why**: Reason for the changes
- **How**: Implementation approach (if complex)
- **Testing**: How you tested the changes
- **Breaking Changes**: Any breaking changes (if applicable)

### Checklist

- [ ] Code follows existing style and patterns
- [ ] Tests added for new functionality
- [ ] Documentation updated (if needed)
- [ ] Commit messages follow conventional format
- [ ] All tests pass
- [ ] No breaking changes (unless intentional and documented)

## Code Style

### Python

- Follow PEP 8 style guidelines
- Use type hints where appropriate
- Write docstrings for public functions and classes
- Keep functions focused and small
- Use meaningful variable and function names

### Documentation

- Update relevant documentation for changes
- Use clear, concise language
- Include code examples where helpful
- Keep README.md up to date

## Testing

### Setup Wobble Testing Framework

This template uses **Wobble** as the standard testing framework for CrackingShells organization.

**Installation:**
```bash
# Install Wobble from repository
pip install git+https://github.com/CrackingShells/Wobble.git

# For development/editable installation
git clone https://github.com/CrackingShells/Wobble.git
cd Wobble
pip install -e .
```

**Add to pyproject.toml dependencies:**
```toml
[project]
dependencies = [
    "wobble @ git+https://github.com/CrackingShells/Wobble.git",
    # ... other dependencies
]
```

### Running Tests with Wobble

```bash
# Run all tests
wobble

# Run specific test categories
wobble --category regression
wobble --category integration
wobble --category development

# File output for CI/CD
wobble --log-file test_results.json --log-file-format json

# Detailed output with file logging
wobble --log-file detailed_results.json --log-verbosity 3

# Exclude slow tests during development
wobble --exclude-slow --category development
```

### Legacy unittest Support

For backward compatibility during migration:
```bash
# Legacy unittest (deprecated)
python -m unittest discover tests

# Run specific test file
python -m unittest tests.test_basic

# Run with verbose output
python -m unittest discover tests -v
```

### Writing Tests

**Test Structure Requirements:**
- Use hierarchical directory structure: `tests/regression/`, `tests/integration/`, `tests/development/`
- Apply required categorization decorators from wobble
- Follow `test_*.py` naming convention
- Use unittest framework as base (wobble extends unittest)

**Test Categorization:**
```python
from wobble.decorators import regression_test, integration_test, development_test

@regression_test
def test_existing_functionality(self):
    """Test that existing features continue to work"""
    pass

@integration_test(scope="component")
def test_component_integration(self):
    """Test component interactions"""
    pass

@development_test(phase=1)
def test_new_feature_development(self):
    """Test new features under development"""
    pass
```

**Best Practices:**
- Add tests for new features with appropriate categorization
- Test edge cases and error conditions
- Use descriptive test names that explain the scenario
- Follow existing test patterns in the repository
- Include file output testing for CI/CD integration

## Release Process

Releases are fully automated using semantic-release and published to PyPI:

1. **Commits are analyzed** for conventional commit format
2. **Version is calculated** based on commit types
3. **Changelog is generated** from commit messages
4. **Version files are updated** (pyproject.toml, CHANGELOG.md)
5. **Changes are committed** back to repository using GitHub App
6. **GitHub release is created** with release notes and tags
7. **Package is built** (wheel and source distribution)
8. **Published to PyPI** using Trusted Publishing (OIDC)

### Version Impact

- `feat:` commits → Minor version (0.1.0 → 0.2.0)
- `fix:` commits → Patch version (0.1.0 → 0.1.1)
- `feat!:` or `BREAKING CHANGE:` → Major version (0.1.0 → 1.0.0)
- Other types → No release

### PyPI Publishing

The project uses PyPI Trusted Publishing for secure, automated package publishing. No API tokens are required.

**For Repository Administrators**: See [PyPI Setup Documentation](../docs/articles/devs/pypi-setup.md) for configuration details.

**Branch Strategy**:
- **main branch**: Production releases (e.g., v1.0.0) published to PyPI
- **dev branch**: Pre-releases (e.g., v1.0.0-dev.1) published to PyPI with pre-release flag

## Getting Help

- **Issues**: Report bugs or request features via GitHub Issues
- **Discussions**: Ask questions in GitHub Discussions
- **Documentation**: Check existing documentation for guidance
- **Code**: Look at existing code for patterns and examples

## Code of Conduct

- Be respectful and inclusive
- Focus on constructive feedback
- Help others learn and grow
- Follow GitHub's community guidelines

Thank you for contributing to mcp-langfuse! 🚀
