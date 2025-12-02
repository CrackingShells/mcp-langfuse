# Getting Started

This article covers:
- Installing {{PROJECT_NAME}}
- Basic usage examples
- Next steps for learning more

## Installation

### From PyPI

Install {{PROJECT_NAME}} using pip:

```bash
pip install {{PACKAGE_NAME}}
```

### From Source

Clone the repository and install in development mode:

```bash
git clone https://github.com/crackingshells/{{PROJECT_NAME}}.git
cd {{PROJECT_NAME}}
pip install -e .
```

## Basic Usage

Import and use {{PACKAGE_NAME}} in your Python code:

```python
from {{PACKAGE_NAME}} import hello_world

# Call the function
result = hello_world()
print(result)
```

### Using the Example Class

```python
from {{PACKAGE_NAME}}.core import ExampleClass

# Create an instance
example = ExampleClass(name="World")

# Use the class methods
greeting = example.greet()
print(greeting)
```

## Next Steps

- Explore the [API Reference](../api/index.md) for detailed documentation of all modules and functions
- Review the [Glossary](../appendices/glossary.md) for terminology definitions
- Additional tutorials will be added as the project grows

## Getting Help

If you encounter issues or have questions:

- Review the API documentation for detailed function signatures and parameters
- Check the appendices for foundational concepts
- Consult the developer documentation for contribution guidelines
