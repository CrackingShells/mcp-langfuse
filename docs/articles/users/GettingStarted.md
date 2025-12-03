# Getting Started

This article covers:
- Installing mcp-langfuse
- Basic usage examples
- Next steps for learning more

## Installation

### From PyPI

Install mcp-langfuse using pip:

```bash
pip install mcp_langfuse
```

### From Source

Clone the repository and install in development mode:

```bash
git clone https://github.com/crackingshells/mcp-langfuse.git
cd mcp-langfuse
pip install -e .
```

## Basic Usage

Import and use mcp_langfuse in your Python code:

```python
from mcp_langfuse import hello_world

# Call the function
result = hello_world()
print(result)
```

### Using the Example Class

```python
from mcp_langfuse.core import ExampleClass

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
