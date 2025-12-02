"""Basic tests for {{PROJECT_NAME}}.

This module contains fundamental tests to ensure the package works correctly.
Tests use unittest framework for compatibility with the future wobble testing system.
"""

import unittest
import sys
from pathlib import Path

# Add the parent directory to the path for imports during testing
sys.path.insert(0, str(Path(__file__).parent.parent))


class TestBasicFunctionality(unittest.TestCase):
    """Test basic package functionality."""

    def test_package_import(self):
        """Test that the main package can be imported successfully."""
        try:
            import {{PACKAGE_NAME}}
            self.assertIsNotNone({{PACKAGE_NAME}})
        except ImportError as e:
            self.fail(f"Failed to import {{PACKAGE_NAME}}: {e}")

    def test_package_has_version(self):
        """Test that the package has a version attribute."""
        import {{PACKAGE_NAME}}

        # Check if package has __version__ attribute
        if hasattr({{PACKAGE_NAME}}, '__version__'):
            self.assertIsInstance({{PACKAGE_NAME}}.__version__, str)
            self.assertGreater(len({{PACKAGE_NAME}}.__version__), 0)
        else:
            # If no __version__, that's okay for minimal packages
            self.skipTest("Package does not define __version__ (acceptable for minimal packages)")

    def test_package_structure(self):
        """Test that the package has expected structure."""
        import {{PACKAGE_NAME}}

        # Package should be importable and have a file path
        self.assertTrue(hasattr({{PACKAGE_NAME}}, '__file__'))

        # Package file should exist
        package_file = Path({{PACKAGE_NAME}}.__file__)
        self.assertTrue(package_file.exists())


class TestProjectConfiguration(unittest.TestCase):
    """Test project configuration and metadata."""

    def test_pyproject_toml_exists(self):
        """Test that pyproject.toml exists and is readable."""
        pyproject_path = Path(__file__).parent.parent / "pyproject.toml"
        self.assertTrue(pyproject_path.exists(), "pyproject.toml should exist")

        # Test that it's readable
        try:
            content = pyproject_path.read_text()
            self.assertGreater(len(content), 0, "pyproject.toml should not be empty")
        except Exception as e:
            self.fail(f"Failed to read pyproject.toml: {e}")

    def test_readme_exists(self):
        """Test that README.md exists and is readable."""
        readme_path = Path(__file__).parent.parent / "README.md"
        self.assertTrue(readme_path.exists(), "README.md should exist")

        # Test that it's readable and not empty
        try:
            content = readme_path.read_text()
            self.assertGreater(len(content), 0, "README.md should not be empty")
        except Exception as e:
            self.fail(f"Failed to read README.md: {e}")

    def test_license_exists(self):
        """Test that LICENSE file exists."""
        license_path = Path(__file__).parent.parent / "LICENSE"
        self.assertTrue(license_path.exists(), "LICENSE file should exist")


if __name__ == '__main__':
    # Run tests with verbose output
    unittest.main(verbosity=2)
