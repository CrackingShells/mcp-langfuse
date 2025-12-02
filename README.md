# {{PROJECT_NAME}}

{{PROJECT_DESCRIPTION}}

## Installation

### From Source

```bash
git clone https://github.com/CrackingShells/{{PROJECT_NAME}}.git
cd {{PROJECT_NAME}}
pip install -e .
```

### From PyPI (when available)

```bash
pip install {{PROJECT_NAME}}
```

## Quick Start

```python
import {{PACKAGE_NAME}}

# Add basic usage example here
```

## Development

### Setup Development Environment

```bash
# Clone the repository
git clone https://github.com/CrackingShells/{{PROJECT_NAME}}.git
cd {{PROJECT_NAME}}

# Install in development mode
pip install -e .

# Install Node.js dependencies for semantic release
npm install
```

### Running Tests

```bash
# Run all tests
python -m unittest discover tests

# Run specific test file
python -m unittest tests.test_basic
```

### Code Quality Tools

Set up automated code quality checks:

```bash
# Install development dependencies
pip install -e .[dev]

# Set up pre-commit hooks
pre-commit install

# Run all checks manually
pre-commit run --all-files
```

Once installed, pre-commit hooks will run automatically on every `git commit` to ensure code quality.

### Building Documentation

Build and serve documentation locally:

```bash
# Serve documentation locally with live reload
mkdocs serve

# Build documentation for production
mkdocs build
```

Documentation is automatically published to ReadTheDocs when changes are pushed to the repository.

### Making Commits

We use [Conventional Commits](https://www.conventionalcommits.org/) for automated versioning:

```bash
# Use commitizen for guided commits
npm run commit

# Or commit manually with conventional format
git commit -m "feat: add new feature"
git commit -m "fix: resolve issue with X"
git commit -m "docs: update README"
```

## Contributing

We welcome contributions! Please see our [Contributing Guide](./CONTRIBUTING.md) for details on:

- Development workflow
- Code style guidelines
- Testing requirements
- Pull request process

## License

This project is licensed under the GNU Affero General Public License v3 - see the [LICENSE](LICENSE) file for details.

## Links

- **Homepage**: https://github.com/CrackingShells/{{PROJECT_NAME}}
- **Bug Reports**: https://github.com/CrackingShells/{{PROJECT_NAME}}/issues
- **Documentation**: https://crackingshells.github.io/{{PROJECT_NAME}}/
