"""Core functionality for mcp-langfuse.

This module contains the main functionality of the mcp_langfuse package.
It provides essential classes and functions that demonstrate best practices
for Python package development, including proper documentation, type hints,
and example usage patterns.

The module serves as a template for building your own functionality. Replace
the example implementations with your actual business logic while maintaining
the documentation standards demonstrated here.

Typical usage example:

    ```python
    from mcp_langfuse.core import hello_world, ExampleClass

    # Simple function usage
    message = hello_world()
    print(message)  # Output: Hello from mcp-langfuse!

    # Class instantiation and usage
    example = ExampleClass("World")
    greeting = example.greet()
    print(greeting)  # Output: Hello, World! Welcome to mcp-langfuse.
    ```

Classes:
    ExampleClass: A demonstration class showing proper documentation and structure.

Functions:
    hello_world: Returns a greeting message to verify package functionality.
"""


def hello_world() -> str:
    """Return a simple greeting message.

    This is a placeholder function to demonstrate basic package structure
    and proper documentation. It serves as a minimal example of a public
    function with complete Google-style docstrings.

    Replace this with your actual functionality while maintaining the
    documentation standards shown here.

    Returns:
        str: A greeting message containing the project name.

    Example:
        Basic usage:

        ```python
        from mcp_langfuse.core import hello_world

        message = hello_world()
        print(message)
        # Output: Hello from mcp-langfuse!
        ```
    """
    return "Hello from mcp-langfuse!"


class ExampleClass:
    """Example class to demonstrate package structure and documentation.

    This is a placeholder class that demonstrates proper Google-style
    documentation for classes, including attributes, methods, and usage
    examples. It shows how to document initialization, instance methods,
    and special methods like __str__ and __repr__.

    Replace this class with your actual implementation while maintaining
    the documentation patterns demonstrated here.

    Attributes:
        name (str): The name associated with this instance. Used to
            personalize greeting messages and identify the instance.

    Example:
        Basic usage:

        ```python
        from mcp_langfuse.core import ExampleClass

        # Create an instance with default name
        example1 = ExampleClass()
        print(example1.greet())
        # Output: Hello, mcp-langfuse! Welcome to mcp-langfuse.

        # Create an instance with custom name
        example2 = ExampleClass("World")
        print(example2.greet())
        # Output: Hello, World! Welcome to mcp-langfuse.

        # String representation
        print(example2)
        # Output: ExampleClass(name='World')
        ```
    """

    def __init__(self, name: str = "mcp-langfuse"):
        """Initialize the ExampleClass instance.

        Creates a new instance of ExampleClass with the specified name.
        The name is stored as an instance attribute and used by the
        greet() method to generate personalized messages.

        Args:
            name (str, optional): The name to associate with this instance.
                Defaults to "mcp-langfuse" if not specified. This name
                will be used in greeting messages and string representations.

        Example:
            ```python
            # Create with default name
            example1 = ExampleClass()

            # Create with custom name
            example2 = ExampleClass("Alice")
            ```
        """
        self.name = name

    def greet(self) -> str:
        """Return a personalized greeting message.

        Generates a greeting message that includes the instance's name
        and welcomes them to the project. This method demonstrates how
        to document instance methods that use instance attributes.

        Returns:
            str: A personalized greeting message in the format
                "Hello, {name}! Welcome to mcp-langfuse." where
                {name} is the instance's name attribute.

        Example:
            Basic usage:

            ```python
            example = ExampleClass("World")
            greeting = example.greet()
            print(greeting)
            # Output: Hello, World! Welcome to mcp-langfuse.

            # With default name
            default_example = ExampleClass()
            print(default_example.greet())
            # Output: Hello, mcp-langfuse! Welcome to mcp-langfuse.
            ```
        """
        return f"Hello, {self.name}! Welcome to mcp-langfuse."

    def __str__(self) -> str:
        """Return string representation of the instance.

        Provides a human-readable string representation of the ExampleClass
        instance, showing the class name and the name attribute value.

        Returns:
            str: String representation in the format "ExampleClass(name='...')".

        Example:
            ```python
            example = ExampleClass("Test")
            print(str(example))
            # Output: ExampleClass(name='Test')
            ```
        """
        return f"ExampleClass(name='{self.name}')"

    def __repr__(self) -> str:
        """Return detailed string representation of the instance.

        Provides a detailed string representation that could be used to
        recreate the instance. In this implementation, it's identical to
        __str__ but could be extended to include more technical details.

        Returns:
            str: Detailed string representation in the format
                "ExampleClass(name='...')".

        Example:
            ```python
            example = ExampleClass("Test")
            print(repr(example))
            # Output: ExampleClass(name='Test')
            ```
        """
        return f"ExampleClass(name='{self.name}')"
