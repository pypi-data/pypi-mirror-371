"""Configuration parser implementations module.

This module provides concrete implementations of configuration parsers for
specific file formats. Currently, it supports YAML and JSON formats.

The module includes:
- YamlParser: A parser for YAML format configuration files
- JsonParser: A parser for JSON format configuration files
"""
from typing import Any, TextIO

from .base_parser import BaseConfigParser, config_parser


@config_parser("yaml", override=False)
@config_parser("yml", override=False)
class YamlParser(BaseConfigParser):
    """Parser for YAML format configuration files.

    This parser handles both .yaml and .yml file extensions.
    """

    @classmethod
    def parse(cls, f: TextIO) -> dict[str, Any]:
        """Parse YAML configuration data from a text stream.

        Args:
            f: A text stream containing YAML configuration data.

        Returns:
            dict[str, Any]: A dictionary containing configuration key-value pairs.

        Raises:
            yaml.YAMLError: If there is an error parsing the YAML data.
        """
        import yaml
        return yaml.safe_load(f)

    @classmethod
    def dump(cls, data: dict[str, Any], f: TextIO) -> None:
        """Write configuration data to a text stream in YAML format.

        Args:
            data: A dictionary containing configuration key-value pairs.
            f: A text stream to write the configuration data to.

        Raises:
            yaml.YAMLError: If there is an error dumping the data to YAML.
        """
        import yaml
        yaml.dump(data, f)

    @classmethod
    def parse_str(cls, data: str) -> dict[str, Any]:
        """Parse YAML configuration data from a string.

        Args:
            data: A string containing YAML configuration data.

        Returns:
            dict[str, Any]: A dictionary containing configuration key-value pairs.

        Raises:
            yaml.YAMLError: If there is an error parsing the YAML data.
        """
        import yaml
        return yaml.safe_load(data)

    @classmethod
    def dump_str(cls, data: dict[str, Any]) -> str:
        """Convert configuration data to a YAML string.

        Args:
            data: A dictionary containing configuration key-value pairs.

        Returns:
            str: A string representation of the configuration data in YAML format.

        Raises:
            yaml.YAMLError: If there is an error dumping the data to YAML.
        """
        import yaml
        return yaml.dump(data)


@config_parser("json", override=False)
class JsonParser(BaseConfigParser):
    """Parser for JSON format configuration files."""

    @classmethod
    def parse(cls, f: TextIO) -> dict[str, Any]:
        """Parse JSON configuration data from a text stream.

        Args:
            f: A text stream containing JSON configuration data.

        Returns:
            dict[str, Any]: A dictionary containing configuration key-value pairs.

        Raises:
            json.JSONDecodeError: If there is an error parsing the JSON data.
        """
        import json
        return json.load(f)

    @classmethod
    def dump(cls, data: dict[str, Any], f: TextIO) -> None:
        """Write configuration data to a text stream in JSON format.

        Args:
            data: A dictionary containing configuration key-value pairs.
            f: A text stream to write the configuration data to.

        Raises:
            TypeError: If the data contains objects that cannot be serialized to JSON.
        """
        import json
        json.dump(data, f, indent=4, ensure_ascii=False)

    @classmethod
    def parse_str(cls, data: str) -> dict[str, Any]:
        """Parse JSON configuration data from a string.

        Args:
            data: A string containing JSON configuration data.

        Returns:
            dict[str, Any]: A dictionary containing configuration key-value pairs.

        Raises:
            json.JSONDecodeError: If there is an error parsing the JSON data.
        """
        import json
        return json.loads(data)

    @classmethod
    def dump_str(cls, data: dict[str, Any]) -> str:
        """Convert configuration data to a JSON string.

        Args:
            data: A dictionary containing configuration key-value pairs.

        Returns:
            str: A string representation of the configuration data in JSON format.

        Raises:
            TypeError: If the data contains objects that cannot be serialized to JSON.
        """
        import json
        return json.dumps(data, indent=4, ensure_ascii=False)