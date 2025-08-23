import typing

import ast
import inspect
import os


def find_typevars_bound_by_class(bound_class):
    """
    Find all TypeVar objects from the typing module that are bound by the specified class.

    Args:
        bound_class: The class to check for as a bound

    Returns:
        A list of TypeVar objects bound by the specified class
    """
    bound_typevars = []

    # Inspect all objects in the typing module
    for name, obj in inspect.getmembers(typing):
        # Check if the object is a TypeVar
        if isinstance(obj, typing.TypeVar):
            # Check if the TypeVar has a bound and if it's the specified class
            if hasattr(obj, "__bound__") and obj.__bound__ is bound_class:
                bound_typevars.append(obj)

    return bound_typevars


class TypeVarVisitor(ast.NodeVisitor):
    def __init__(self, bound_class_name):
        self.bound_class_name = bound_class_name
        self.found_typevars = []

    def visit_Call(self, node):
        # Check if this is a TypeVar creation
        if isinstance(node.func, ast.Name) and node.func.id == "TypeVar":
            # Look for bound argument
            for keyword in node.keywords:
                if (
                    keyword.arg == "bound"
                    and isinstance(keyword.value, ast.Name)
                    and keyword.value.id == self.bound_class_name
                ):
                    # Get the TypeVar name if possible
                    if len(node.args) > 0 and isinstance(
                        node.args[0], ast.Constant
                    ):
                        self.found_typevars.append(node.args[0].value)

        # Continue traversing the AST
        self.generic_visit(node)


def find_typevars_in_file(file_path, bound_class_name):
    with open(file_path, encoding="utf-8") as file:
        try:
            tree = ast.parse(file.read())
            visitor = TypeVarVisitor(bound_class_name)
            visitor.visit(tree)
            return visitor.found_typevars
        except SyntaxError:
            return []


def find_typevars_in_directory(directory, bound_class_name):
    results = {}

    for root, _, files in os.walk(directory):
        for file in files:
            if file.endswith(".py"):
                file_path = os.path.join(root, file)
                typevars = find_typevars_in_file(file_path, bound_class_name)
                if typevars:
                    results[file_path] = typevars

    return results


# Example usage
if __name__ == "__main__":
    # Replace with your directory and the class name you're looking for
    directory = "../ss"
    bound_class = "TransformerConfig"  # The class name as a string

    results = find_typevars_in_directory(directory, bound_class)

    if results:
        print(f"Found TypeVars bound by {bound_class}:")
        for file_path, typevars in results.items():
            print(f"  {file_path}: {typevars}")
    else:
        print(f"No TypeVars bound by {bound_class} found.")
