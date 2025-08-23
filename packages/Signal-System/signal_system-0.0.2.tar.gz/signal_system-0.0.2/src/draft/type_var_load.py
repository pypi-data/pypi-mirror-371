from typing import Any, Dict, List, Type, TypeVar

import ast
import importlib
import inspect
import os
import sys


class TypeVarCollector(ast.NodeVisitor):
    """Visitor to collect TypeVar definitions with specific bounds."""

    def __init__(self, bound_class_name: str):
        self.bound_class_name = bound_class_name
        self.typevar_definitions = []
        self.imports = {}

    def visit_Import(self, node):
        """Track regular imports."""
        for name in node.names:
            if name.asname:
                self.imports[name.asname] = name.name
            else:
                self.imports[name.name] = name.name
        self.generic_visit(node)

    def visit_ImportFrom(self, node):
        """Track from-imports."""
        if node.module:
            for name in node.names:
                if name.asname:
                    self.imports[name.asname] = f"{node.module}.{name.name}"
                else:
                    self.imports[name.name] = f"{node.module}.{name.name}"
        self.generic_visit(node)

    def visit_Call(self, node):
        """Find TypeVar calls with the specified bound."""
        if isinstance(node.func, ast.Name) and node.func.id == "TypeVar":
            # Look for bound argument
            typevar_name = None
            bound_name = None

            # Get the TypeVar name
            if len(node.args) > 0 and isinstance(node.args[0], ast.Constant):
                typevar_name = node.args[0].value

            # Check for bound parameter
            for keyword in node.keywords:
                if keyword.arg == "bound":
                    if isinstance(keyword.value, ast.Name):
                        bound_name = keyword.value.id
                    elif isinstance(keyword.value, ast.Attribute):
                        # Handle module.Class bound
                        if isinstance(keyword.value.value, ast.Name):
                            module_name = keyword.value.value.id
                            if module_name in self.imports:
                                bound_name = f"{self.imports[module_name]}.{keyword.value.attr}"
                            else:
                                bound_name = (
                                    f"{module_name}.{keyword.value.attr}"
                                )

            if typevar_name and bound_name:
                self.typevar_definitions.append(
                    {"name": typevar_name, "bound": bound_name, "node": node}
                )

        self.generic_visit(node)


def get_bounded_type_vars(
    directory: str, bound_class: type
) -> dict[str, list[TypeVar]]:
    """
    Scan a directory for TypeVar definitions bound by a specific class and load the actual instances.

    Args:
        directory: Directory path to scan
        bound_class: The class object to check for as a bound

    Returns:
        Dictionary mapping file paths to lists of TypeVar instances
    """

    results = {}
    bound_class_name = bound_class.__name__
    # bound_module_name = bound_class.__module__
    # full_bound_name = f"{bound_module_name}.{bound_class_name}"

    # First pass: Scan files to find all TypeVar definitions
    typevar_definitions = {}

    for root, _, files in os.walk(directory):
        for file in files:
            if file.endswith(".py"):
                file_path = os.path.join(root, file)

                # Parse the file
                try:
                    with open(file_path, encoding="utf-8") as f:
                        tree = ast.parse(f.read(), filename=file_path)

                    # Collect TypeVar definitions
                    collector = TypeVarCollector(bound_class_name)
                    collector.visit(tree)

                    # Save found definitions
                    if collector.typevar_definitions:
                        print(collector.typevar_definitions)
                        typevar_definitions[file_path] = (
                            collector.typevar_definitions
                        )
                except (SyntaxError, UnicodeDecodeError):
                    continue

    # Second pass: Try to import modules and retrieve TypeVar instances
    for file_path, definitions in typevar_definitions.items():
        # Convert file path to module path
        rel_path = os.path.relpath(file_path, directory)
        module_path = os.path.splitext(rel_path)[0].replace(os.path.sep, ".")

        # Skip if module path is invalid
        if not all(part.isidentifier() for part in module_path.split(".")):
            continue

        try:
            # Temporarily add directory to path
            sys.path.insert(0, directory)

            # Try to import the module
            module = importlib.import_module(module_path)

            # Check each TypeVar in the module
            found_typevars = []

            for item_name, item in inspect.getmembers(module):
                if (
                    isinstance(item, TypeVar)
                    and hasattr(item, "__bound__")
                    and item.__bound__ is bound_class
                ):
                    found_typevars.append(item)

            if found_typevars:
                results[file_path] = found_typevars

        except (ImportError, AttributeError, ValueError):
            # Skip if module cannot be imported
            continue
        finally:
            # Clean up sys.path
            if directory in sys.path:
                sys.path.remove(directory)

    return results


# Example usage
if __name__ == "__main__":
    from ss.utility.learning.parameter.transformer.config import (
        TransformerConfig,
    )

    # Replace with your directory and bound class
    project_directory = "../ss"

    # Find TypeVars bound by str
    bounded_type_vars = get_bounded_type_vars(
        project_directory, TransformerConfig
    )

    if bounded_type_vars:
        print(f"Found TypeVar:")
        for file_path, typevars in bounded_type_vars.items():
            print(f"  {file_path}:")
            for typevar in typevars:
                print(f"    {typevar.__name__} = {typevar}")
    else:
        print("No TypeVar found.")
