"""Configuration source module.

This module provides abstract and concrete implementations for configuration sources.
A configuration source is responsible for parsing configuration data from various
locations such as files or command-line arguments.
"""
import sys
from abc import ABC, abstractmethod
from pathlib import Path
from typing import Any

from .parser.base_parser import get_config_parser


class BaseSource(ABC):
    """Abstract base class for configuration sources.

    All configuration sources must inherit from this class and implement the
    parse() method.
    """

    @abstractmethod
    def parse(self) -> dict[str, Any]:
        """Parse configuration data from the source.

        Returns:
            dict[str, Any]: A dictionary containing configuration key-value pairs.
        """
        ...


class FileSource(BaseSource):
    """Configuration source that reads from a file.

    This source parses configuration data from a file using the appropriate
    parser based on the file extension.
    """

    def __init__(self, path: Path | str | None = None, path_from_1st_arg: bool = False) -> None:
        """Initialize a FileSource instance.

        Args:
            path: The path to the configuration file. If None and path_from_1st_arg
                is True, the first command-line argument will be used as the path.
            path_from_1st_arg: Whether to use the first command-line argument as
                the file path.

        Raises:
            ValueError: If path is None and path_from_1st_arg is False.
            FileNotFoundError: If the specified configuration file does not exist.
        """
        if path_from_1st_arg:
            path = sys.argv[1]
        if path is None:
            raise ValueError("Path is None. Please provide a path to the config file, or set path_from_1st_arg=True.")
        if isinstance(path, str):
            path = Path(path)

        if not path.exists():
            raise FileNotFoundError(f"Config file {path} not found.")

        self.file_path = path
        self.suffix = path.suffix[1:].lower()

    def parse(self) -> dict[str, Any]:
        """Parse configuration data from the file.

        Returns:
            dict[str, Any]: A dictionary containing configuration key-value pairs.

        Raises:
            ValueError: If the file format is not supported.
        """
        parser = get_config_parser(self.suffix)
        if parser is None:
            raise ValueError(f"Unsupported config file format: {self.suffix}")
        with open(self.file_path) as f:
            return parser.parse(f)


class CliSource(BaseSource):
    """Configuration source that reads from command-line arguments.

    This source parses configuration data from command-line arguments using a
    specified prefix.
    """

    def __init__(self, prefix: str = "--", args: list[str] | None = None):
        """Initialize a CliSource instance.

        Args:
            prefix: The prefix for command-line arguments (default: "--").
            args: A list of command-line arguments. If None, sys.argv[1:] will be used.
        """
        self.prefix = prefix
        self.args = args or sys.argv[1:]

    def parse(self) -> dict[str, Any]:
        """Parse configuration data from command-line arguments.

        Returns:
            dict[str, Any]: A dictionary containing configuration key-value pairs.

        Note:
            Supports three formats for arguments:
            1. "--key=value"
            2. "--key value"
            3. "--key" (sets value to None)
        """
        config: dict[str, Any] = {}
        args = self.args.copy()  # 创建一个副本以便修改
        i = 0
        
        while i < len(args):
            arg = args[i]
            if not arg.startswith(self.prefix):
                i += 1
                continue
                
            key = arg[len(self.prefix) :]
            i += 1
            
            # case 1: "key=value"
            if "=" in key:
                k, v = key.split("=", 1)
                config[k] = v
            else:
                if i < len(args) and not args[i].startswith(self.prefix):
                    # case 2: "key value"
                    config[key] = args[i]
                    i += 1
                else:
                    # case 3: "key"
                    config[key] = None
        
        return config

        return config
