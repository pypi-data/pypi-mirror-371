from typing import Set, Type, TypeVar

import importlib
import inspect
import pkgutil

from ss.utility.logging import Logging

logger = Logging.get_logger(__name__)


class Package:
    imported_packages: Set[str] = set()

    @classmethod
    def import_submodules(
        cls, module_name: str, parent_module_name: str = ""
    ) -> None:
        """
        Import all submodules of a module recursively

        Arguments
        ---------
        module_name: str
            The module name to import submodules of
        parent_module_name: str
            The parent module name
        """
        # Check if the module has already been imported
        if module_name in cls.imported_packages:
            return

        # Import the module
        module_name = (
            f"{parent_module_name}.{module_name}"
            if parent_module_name
            else module_name
        )
        module = importlib.import_module(module_name)

        # Check if module is a package
        if hasattr(module, "__path__"):
            # Iterate through all submodules
            submodule_name_list = []
            for _, submodule_name, _ in pkgutil.walk_packages(module.__path__):
                names = submodule_name.split(".")
                # FIXME: Not sure why some submodule_name are in the format of
                # "some_module_name.module_name" and some are in the format of
                # "module_name". This is a temporary fix to avoid the former.
                if len(names) > 1:
                    continue
                submodule_name_list.append(submodule_name)
            for submodule_name in submodule_name_list:
                cls.import_submodules(
                    module_name=f"{submodule_name}",
                    parent_module_name=module_name,
                )

        # Add the loaded module name to the imported packages
        if parent_module_name:
            cls.imported_packages.add(module_name)

    @staticmethod
    def resolve_module_name(module_name: str) -> str:
        """
        Resolve the module name to the full module path

        Arguments
        ---------
        module_name: str
            The module name to resolve

        Returns
        -------
        full_module_name: str
            The full module path
        """
        # names = module_name.split(".")
        # if len(names) == 1:
        #     return module_name
        # module_name = names[0]
        # for name in names[1:]:
        #     if name[0] == "_":
        #         break
        #     module_name = f"{module_name}.{name}"

        return module_name

    @staticmethod
    def get_subclasses(base_class: Type) -> Set[Type]:
        """
        Get all subclasses recursively

        Arguments
        ---------
        cls: Type
            The base class to find subclasses of


        Returns
        -------
        subclasses: Set[Type]
            Set of all subclasses
        """
        subclasses = set()
        for subclass in base_class.__subclasses__():
            subclasses.add(subclass)
            subclasses.update(Package.get_subclasses(subclass))
        return subclasses

    # @staticmethod
    # def get_bounded_type_var(bound_class: Type) -> Set[TypeVar]:
    #     """
    #     Get all bounded type variables recursively

    #     Arguments
    #     ---------
    #     bound_class: Type
    #         The base class to find bounded type variables of

    #     Returns
    #     -------
    #     bounded_type_vars: Set[TypeVar]
    #         Set of all bounded type variables
    #     """
    #     bounded_type_vars = set()
    #     # Inspect all objects in the typing module
    #     for name, obj in inspect.getmembers(typing):
    #         print(name, obj)

    #         # Check if the object is a TypeVar
    #         if isinstance(obj, TypeVar):
    #             # Check if the TypeVar has a bound and if it's the specified class
    #             if hasattr(obj, "__bound__") and obj.__bound__ is bound_class:
    #                 bounded_type_vars.add(obj)

    #     return bounded_type_vars
