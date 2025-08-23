from typing import Any, Dict, Type, TypeVar

from dataclasses import dataclass, fields

from ss.utility.logging import Logging

logger = Logging.get_logger(__name__)

BLC = TypeVar("BLC", bound="BaseLearningConfig")


@dataclass
class BaseLearningConfig:

    @classmethod
    def reload(
        cls: Type[BLC], config: BLC, name: str = "config", level: int = 0
    ) -> BLC:
        """
        Reload the configuration to ensure that the configuration is updated.
        """
        # Do not use asdict(self) method for conversion because it does not work
        # for different versions due to inconsistent arguments. Instead, use the
        # meta method self.__dict__.

        if level == 0:
            logger.debug("")
            logger.debug("Loading configuration...")
        config_init_arguments: Dict[str, Any] = {}
        config_private_attributes: Dict[str, Any] = {}
        indent_level = level + 1

        logger.debug(logger.indent(indent_level) + f"{name} = " + cls.__name__)

        init_arguments = [_field.name for _field in fields(cls)]

        for key, value in config.__dict__.items():
            # TODO: The following condition did not check the dunder attributes
            is_init_argument = True
            if key.startswith("__"):
                continue
            if key.startswith("_"):
                key = key[1:]
                is_init_argument = False
            if key not in init_arguments:
                is_init_argument = False

            if isinstance(value, BaseLearningConfig):
                value = type(value).reload(value, name=key, level=level + 1)
            elif isinstance(value, (tuple, list)):
                _value = [
                    (
                        type(item).reload(
                            item, name=key + f"[{i}]", level=level + 1
                        )
                        if isinstance(item, BaseLearningConfig)
                        else item
                    )
                    for i, item in enumerate(value)
                ]
                value = tuple(_value) if isinstance(value, tuple) else _value
            else:
                logger.debug(
                    logger.indent(indent_level + 1) + key + " = " + str(value)
                )

            # TODO: Did not check the condition that the key exists
            # in the old version but not in the new version
            if is_init_argument:
                config_init_arguments[key] = value
            else:
                config_private_attributes[key] = value

        # Create a new instance of the configuration class
        config = cls(**config_init_arguments)

        # Set private attribute through the property setter
        for key, value in config_private_attributes.items():
            if hasattr(config, key):
                setattr(config, key, value)

        return config

    # def __str__(self) -> str:
    #     """Pretty print with proper indentation for nested dataclasses"""
    #     return self._pretty_print(0)

    # def _pretty_print(self, indent_level: int = 0) -> str:
    #     """Recursively pretty print nested dataclasses"""
    #     indent = "  " * indent_level
    #     next_indent = "  " * (indent_level + 1)

    #     result = f"{self.__class__.__name__}(\n"

    #     for field in fields(self):
    #         value = getattr(self, field.name)

    #         if isinstance(value, BaseLearningConfig):
    #             # Handle other BaseLearningConfig instances
    #             value_str = value._pretty_print(indent_level + 1)
    #         elif hasattr(value, '__dataclass_fields__'):
    #             # Handle other dataclasses that don't inherit from BaseLearningConfig
    #             value_str = self._format_generic_dataclass(value, indent_level + 1)
    #         else:
    #             # Handle regular values (primitives, enums, etc.)
    #             value_str = repr(value)

    #         result += f"{next_indent}{field.name}={value_str},\n"

    #     result += f"{indent})"
    #     return result

    # def _format_generic_dataclass(self, obj: Any, indent_level: int) -> str:
    #     """Format dataclasses that don't inherit from BaseLearningConfig"""
    #     if not hasattr(obj, '__dataclass_fields__'):
    #         return repr(obj)

    #     indent = "  " * indent_level
    #     next_indent = "  " * (indent_level + 1)

    #     result = f"{obj.__class__.__name__}(\n"

    #     for field in fields(obj):
    #         value = getattr(obj, field.name)

    #         if isinstance(value, BaseLearningConfig):
    #             value_str = value._pretty_print(indent_level + 1)
    #         elif hasattr(value, '__dataclass_fields__'):
    #             value_str = self._format_generic_dataclass(value, indent_level + 1)
    #         else:
    #             value_str = repr(value)

    #         result += f"{next_indent}{field.name}={value_str},\n"

    #     result += f"{indent})"
    #     return result
