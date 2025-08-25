"""Base configuration module.

This module provides the BaseConfig class, which is the foundation for creating
configuration classes in the skirk library. It supports loading configurations
from various sources such as files and command-line arguments, and provides
type conversion and validation.
"""

from dataclasses import dataclass
from pathlib import Path
from typing import Any, get_args

from .parser.base_parser import get_config_parser
from .source import CliSource, FileSource
from .type.base_type_factory import get_type_factory


@dataclass
class BaseConfig:
    """Base configuration class.

    For custom configurations, create a sub-class that inherits from this one
    and define dataclass fields for your configuration parameters.

    Attributes:
        None (intended to be extended by subclasses)
    """

    @classmethod
    def of(cls, *sources) -> "BaseConfig":
        """Create a configuration instance from multiple sources.

        Args:
            *sources: Variable length argument list of configuration sources.
                Each source must have a parse() method that returns a dict.

        Returns:
            BaseConfig: An instance of the configuration class.

        Raises:
            TypeError: If any source does not return a dict from its parse() method.
        """
        config_dict = {}
        for i, source in enumerate(sources):
            parsed = source.parse()
            if not isinstance(parsed, dict):
                raise TypeError(f"Source at index {i} must return a dict from .parse(), got {type(parsed).__name__}")
            config_dict.update(parsed)

        return cls(**cls.__type_convertion(config_dict))

    @classmethod
    def __type_convertion(cls, config_dict: dict[str, Any]) -> dict[str, Any]:
        """Convert values in the config dict to the expected types.

        Args:
            config_dict: A dictionary containing configuration values.

        Returns:
            dict[str, Any]: A dictionary with values converted to the expected types.

        Raises:
            ValueError: If a value cannot be converted to the expected type.
        """
        result = {}
        for field, value in config_dict.items():
            if field not in cls.__dataclass_fields__:
                continue
            expected_type = cls.__dataclass_fields__[field].type
            if (isinstance(expected_type, type) and not isinstance(value, expected_type)) or (
                hasattr(expected_type, "__args__")
                and not any(isinstance(value, t) for t in get_args(expected_type) if isinstance(t, type))
            ):
                successed = False
                # Check if expected_type is a single type
                if isinstance(expected_type, type):
                    factory = get_type_factory(expected_type)
                    if factory is not None:
                        result[field] = factory(value)
                        successed = True
                elif hasattr(expected_type, "__args__"):
                    # Handle UnionType or other generic types
                    for type_ in expected_type.__args__:
                        try:
                            factory = get_type_factory(type_)
                            if factory is not None:
                                result[field] = factory(value)
                                successed = True
                                break
                        except (TypeError, ValueError):
                            continue
                    if not successed:
                        raise ValueError(f"Cannot init field {field} from raw str {value}")
            else:
                result[field] = value
        return result

    @classmethod
    def from_file(
        cls,
        path: Path | str | None = None,
        path_from_1st_arg: bool = False,
    ) -> "BaseConfig":
        """Create a configuration instance from a file.

        Args:
            path: The path to the configuration file. If None and path_from_1st_arg
                is True, the first command-line argument will be used as the path.
            path_from_1st_arg: Whether to use the first command-line argument as
                the file path.

        Returns:
            BaseConfig: An instance of the configuration class.
        """
        source = FileSource(path, path_from_1st_arg)
        return cls.of(source)

    @classmethod
    def from_cli(cls, prefix: str = "--", args: list[str] | None = None) -> "BaseConfig":
        """Create a configuration instance from command-line arguments.

        Args:
            prefix: The prefix for command-line arguments (default: "--").
            args: A list of command-line arguments. If None, sys.argv[1:] will be used.

        Returns:
            BaseConfig: An instance of the configuration class.
        """
        source = CliSource(prefix, args)
        return cls.of(source)

    def dump(self, file_path: Path | str) -> None:
        """Dump the configuration to a file.

        Args:
            file_path: The path to the file where the configuration should be dumped.

        Raises:
            ValueError: If the file format is not supported.
        """
        if isinstance(file_path, str):
            file_path = Path(file_path)

        # Remove the dot from the suffix (e.g. '.json' -> 'json')
        suffix = file_path.suffix[1:]
        parser = get_config_parser(suffix)
        if parser is None:
            raise ValueError(f"Unsupported config file format: {file_path.suffix}")
        with open(file_path, "w", encoding="utf-8") as f:
            parser.dump(self.__dict__, f)
