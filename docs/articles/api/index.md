# API Reference

This section provides complete API documentation for mcp-langfuse, auto-generated from code docstrings using mkdocstrings.

## Getting Started

Import the package in your Python code:

```python
import mcp_langfuse
```

Access specific modules:

```python
from mcp_langfuse.core import ExampleClass, hello_world
```

## Using mkdocstrings

This documentation uses mkdocstrings to automatically generate API reference from Python docstrings. Each module page includes:

- Module-level documentation
- Class definitions with attributes and methods
- Function signatures with parameters and return types
- Usage examples from docstrings

To reference API documentation in your own markdown files, use the mkdocstrings syntax:

```markdown
::: mcp_langfuse.module_name
```

This automatically generates formatted documentation for the specified module.

### Options

Customize the output with options:

```markdown
::: mcp_langfuse.module_name
    options:
      show_source: true
      show_root_heading: true
      heading_level: 2
```

## Module Index

### [Core Module](core.md)

The core module provides the main functionality of mcp-langfuse. Includes:

- `hello_world()` - Basic greeting function
- `ExampleClass` - Example class demonstrating structure and documentation

## Code Examples

### Basic Function Usage

```python
from mcp_langfuse import hello_world

result = hello_world()
print(result)  # Output: Hello, World!
```

### Class Instantiation

```python
from mcp_langfuse.core import ExampleClass

# Create instance
example = ExampleClass(name="Developer")

# Call methods
greeting = example.greet()
print(greeting)  # Output: Hello, Developer!
```

## Documentation Standards

All public APIs in mcp-langfuse follow Google-style docstring conventions:

- Brief description on the first line
- Detailed description in subsequent paragraphs
- `Args:` section for parameters
- `Returns:` section for return values
- `Raises:` section for exceptions
- `Example:` section with usage examples

This ensures consistent, high-quality API documentation throughout the project.
