"""Skirk provides a unified interface for loading configuration from various sources,
including files (YAML, JSON) and command-line arguments. It supports type conversion
and validation, making it easy to manage configuration in your applications.
"""

from .base_config import BaseConfig
from .parser.base_parser import BaseConfigParser, config_parser
from .source import BaseSource, CliSource, FileSource
from .type.base_type_factory import type_factory

__version__ = "0.1.0"

__all__ = [
    "BaseConfig",
    "BaseSource",
    "FileSource",
    "CliSource",
    "BaseConfigParser",
    "config_parser",
    "type_factory",
    "__version__",
]