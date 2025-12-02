"""{{PROJECT_NAME}} - {{PROJECT_DESCRIPTION}}

This package provides core functionality for {{PROJECT_NAME}}. It includes
essential classes and functions that form the foundation of the project.

The package is designed to be easy to use while providing powerful capabilities
for [describe your use case here]. All public APIs follow consistent patterns
and include comprehensive documentation.

Typical usage example:

    ```python
    from {{PACKAGE_NAME}}.core import hello_world, ExampleClass

    # Use the hello_world function
    message = hello_world()
    print(message)

    # Create and use an ExampleClass instance
    example = ExampleClass("MyProject")
    greeting = example.greet()
    print(greeting)
    ```

Classes:
    ExampleClass: A demonstration class showing package structure and usage patterns.

Functions:
    hello_world: Returns a simple greeting message to verify package installation.

Attributes:
    __version__ (str): The current version of {{PROJECT_NAME}}, managed by semantic-release.
"""

# Version will be managed by semantic-release
__version__ = "0.1.0"

# Import main functionality here
# Example:
# from .core import main_function
# from .utils import helper_function

# Define what gets imported with "from {{PACKAGE_NAME}} import *"
__all__ = [
    # Add public API functions/classes here
    # Example: "main_function", "helper_function"
]
