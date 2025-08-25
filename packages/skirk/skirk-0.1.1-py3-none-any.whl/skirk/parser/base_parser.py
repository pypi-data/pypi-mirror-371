"""Configuration parser module.

This module provides an abstract base class for configuration parsers and
functions for registering and retrieving parsers based on file suffixes.

The module includes:
- BaseConfigParser: An abstract base class defining the interface for parsers
- config_parser: A decorator for registering parsers
- get_config_parser: A function for retrieving parsers by file suffix
"""
from abc import ABC, abstractmethod
from typing import Any, TextIO

__file_parsers: dict[str, "BaseConfigParser"] = {}


class BaseConfigParser(ABC):
    """Abstract base class for configuration parsers.

    All configuration parsers must inherit from this class and implement the
    parse() method. Other methods (dump, parse_str, dump_str) are optional
    and should be implemented as needed.
    """

    @classmethod
    @abstractmethod
    def parse(cls, f: TextIO) -> dict[str, Any]:
        """Parse configuration data from a text stream.

        Args:
            f: A text stream containing configuration data.

        Returns:
            dict[str, Any]: A dictionary containing configuration key-value pairs.
        """
        ...

    @classmethod
    def dump(cls, data: dict[str, Any], f: TextIO) -> None:
        """Write configuration data to a text stream.

        Args:
            data: A dictionary containing configuration key-value pairs.
            f: A text stream to write the configuration data to.

        Raises:
            NotImplementedError: If the method is not implemented by a subclass.
        """
        raise NotImplementedError(f"dump method not implemented in {cls.__name__}")

    @classmethod
    def parse_str(cls, data: str) -> dict[str, Any]:
        """Parse configuration data from a string.

        Args:
            data: A dictionary containing configuration data.

        Raises:
            NotImplementedError: If the method is not implemented by a subclass.
        """
        raise NotImplementedError(f"parse_str method not implemented in {cls.__name__}")

    @classmethod
    def dump_str(cls, data: dict[str, Any]) -> str:
        """Convert configuration data to a string.

        Args:
            data: A dictionary containing configuration key-value pairs.

        Returns:
            str: A string representation of the configuration data.

        Raises:
            NotImplementedError: If the method is not implemented by a subclass.
        """
        raise NotImplementedError(f"dump_str method not implemented in {cls.__name__}")


def config_parser(suffix: str, override: bool = False):
    """Decorator for registering configuration parsers.

    This decorator registers a class as a parser for files with a specific suffix.

    Args:
        suffix: The file suffix for which the parser is being registered.
        override: Whether to override an existing parser for the same suffix.
            Defaults to False.

    Returns:
        Callable: A decorator function that registers the parser and returns
            the original class.

    Raises:
        ValueError: If a parser for the same suffix is already registered and
            override is False.
    """
    def wrapper(cls):
        if suffix in __file_parsers and not override:
            raise ValueError(f"Parser for suffix {suffix} already registered, set override=True to override")
        __file_parsers[suffix] = cls
        return cls

    return wrapper


def get_config_parser(suffix: str) -> BaseConfigParser | None:
    """Retrieve a configuration parser for the specified file suffix.

    Args:
        suffix: The file suffix for which to retrieve the parser.

    Returns:
        BaseConfigParser | None: The parser for the specified suffix, or None
            if no parser is registered.
    """
    if suffix not in __file_parsers:
        return None
    return __file_parsers[suffix]
