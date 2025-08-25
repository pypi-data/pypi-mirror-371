import os
import sys
import tempfile
from pathlib import Path

import pytest

from skirk.parser.base_parser import BaseConfigParser
from skirk.source import CliSource, FileSource


# Mock parser for testing
class MockParser(BaseConfigParser):
    def parse(self, f):
        return {"name": "Test", "age": 30}

    def dump(self, data, f):
        pass

    def parse_str(self, data):
        return {"name": "Test", "age": 30}

    def dump_str(self, data):
        return "{}"


# Fixture to register mock parser
@pytest.fixture(autouse=True)
def mock_parser_registry(monkeypatch):
    # Mock get_config_parser function to return our MockParser
    def mock_get_config_parser(suffix):
        return MockParser()

    # Mock the get_config_parser function in source module
    monkeypatch.setattr("skirk.source.get_config_parser", mock_get_config_parser)


class TestFileSource:
    def test_init_with_valid_path(self):
        # Create a temporary file
        with tempfile.NamedTemporaryFile(suffix=".test", delete=False) as f:
            temp_file_path = f.name

        try:
            # Test initialization with valid path
            source = FileSource(temp_file_path)
            assert source.file_path == Path(temp_file_path)
            assert source.suffix == "test"
        finally:
            # Clean up
            os.unlink(temp_file_path)

    def test_init_with_path_from_1st_arg(self, monkeypatch):
        # Save original argv
        original_argv = sys.argv.copy()

        try:
            # Create a temporary file
            with tempfile.NamedTemporaryFile(suffix=".test", delete=False) as f:
                temp_file_path = f.name

            # Mock sys.argv
            monkeypatch.setattr("sys.argv", ["script.py", temp_file_path])

            # Test initialization with path_from_1st_arg
            source = FileSource(path_from_1st_arg=True)
            assert source.file_path == Path(temp_file_path)
            assert source.suffix == "test"
        finally:
            # Clean up
            os.unlink(temp_file_path)
            # Restore original argv
            monkeypatch.setattr("sys.argv", original_argv)

    def test_init_with_none_path(self):
        # Test initialization with None path and path_from_1st_arg=False
        with pytest.raises(ValueError) as excinfo:
            FileSource(path=None, path_from_1st_arg=False)
        assert "Path is None" in str(excinfo.value)

    def test_init_with_nonexistent_path(self):
        # Test initialization with nonexistent path
        with pytest.raises(FileNotFoundError) as excinfo:
            FileSource("nonexistent_file.test")
        assert "not found" in str(excinfo.value)

    def test_parse(self):
        # Create a temporary file
        with tempfile.NamedTemporaryFile(suffix=".test", mode="w", delete=False) as f:
            f.write("test content")
            temp_file_path = f.name

        try:
            # Test parse method
            source = FileSource(temp_file_path)
            data = source.parse()
            assert data == {"name": "Test", "age": 30}
        finally:
            # Clean up
            os.unlink(temp_file_path)


class TestCliSource:
    def test_init_with_defaults(self):
        # Test initialization with defaults
        source = CliSource()
        assert source.prefix == "--"
        assert source.args == sys.argv[1:]

    def test_init_with_custom_prefix_and_args(self):
        # Test initialization with custom prefix and args
        args = ["-name", "Test", "-age", "30"]
        source = CliSource(prefix="-", args=args)
        assert source.prefix == "-"
        assert source.args == args

    def test_parse_with_key_value_pairs(self):
        # Test parsing with key=value pairs
        args = ["--name=Test", "--age=30"]
        source = CliSource(args=args)
        data = source.parse()
        assert data == {"name": "Test", "age": "30"}

    def test_parse_with_key_value_separated(self):
        # Test parsing with key and value separated
        args = ["--name", "Test", "--age", "30"]
        source = CliSource(args=args)
        data = source.parse()
        assert data == {"name": "Test", "age": "30"}

    def test_parse_with_flags(self):
        # Test parsing with flags (no value)
        args = ["--verbose", "--debug"]
        source = CliSource(args=args)
        data = source.parse()
        assert data == {"verbose": None, "debug": None}

    def test_parse_with_mixed_formats(self):
        # Test parsing with mixed formats
        args = ["--name=Test", "--age", "30", "--verbose"]
        source = CliSource(args=args)
        data = source.parse()
        assert data == {"name": "Test", "age": "30", "verbose": None}

    def test_parse_without_prefix(self):
        # Test that arguments without prefix are ignored
        args = ["name", "Test", "--age", "30"]
        source = CliSource(args=args)
        data = source.parse()
        assert data == {"age": "30"}
        assert "name" not in data