import io
import json
import tempfile

import pytest
import yaml

from skirk.parser.base_parser import BaseConfigParser, get_config_parser
from skirk.parser.parser_impl import JsonParser, YamlParser


class TestParsers:
    def test_yaml_parser(self):
        # Test YAML parser
        parser = YamlParser

        # Test parse method
        yaml_content = """
name: Test
age: 30
"""
        with io.StringIO(yaml_content) as f:
            data = parser.parse(f)
            assert data == {"name": "Test", "age": 30}

        # Test parse_str method
        data = parser.parse_str(yaml_content)
        assert data == {"name": "Test", "age": 30}

        # Test dump method
        data = {"name": "Test", "age": 30}
        with io.StringIO() as f:
            parser.dump(data, f)
            f.seek(0)
            dumped_data = yaml.safe_load(f)
            assert dumped_data == data

        # Test dump_str method
        dumped_str = parser.dump_str(data)
        dumped_data = yaml.safe_load(dumped_str)
        assert dumped_data == data

    def test_json_parser(self):
        # Test JSON parser
        parser = JsonParser()

        # Test parse method
        json_content = '{"name": "Test", "age": 30}'
        with io.StringIO(json_content) as f:
            data = parser.parse(f)
            assert data == {"name": "Test", "age": 30}

        # Test parse_str method
        data = parser.parse_str(json_content)
        assert data == {"name": "Test", "age": 30}

        # Test dump method
        data = {"name": "Test", "age": 30}
        with io.StringIO() as f:
            parser.dump(data, f)
            f.seek(0)
            dumped_data = json.load(f)
            assert dumped_data == data

        # Test dump_str method
        dumped_str = parser.dump_str(data)
        dumped_data = json.loads(dumped_str)
        assert dumped_data == data

    def test_get_config_parser(self):
        # Test get_config_parser function
        yaml_parser = get_config_parser("yaml")
        assert yaml_parser is YamlParser

        yml_parser = get_config_parser("yml")
        assert yml_parser is YamlParser

        json_parser = get_config_parser("json")
        assert json_parser is JsonParser

        # Test unknown suffix
        unknown_parser = get_config_parser("unknown")
        assert unknown_parser is None

    def test_file_parsing(self):
        # Test parsing from actual files
        # Create temporary YAML file
        with tempfile.NamedTemporaryFile(suffix=".yaml", mode="w", delete=False) as f:
            f.write("name: Test\nage: 30")
            yaml_file_path = f.name

        # Create temporary JSON file
        with tempfile.NamedTemporaryFile(suffix=".json", mode="w", delete=False) as f:
            f.write('{"name": "Test", "age": 30}')
            json_file_path = f.name

        try:
            # Test YAML file parsing
            yaml_parser = get_config_parser("yaml")
            with open(yaml_file_path) as f:
                data = yaml_parser.parse(f)
                assert data == {"name": "Test", "age": 30}

            # Test JSON file parsing
            json_parser = get_config_parser("json")
            with open(json_file_path) as f:
                data = json_parser.parse(f)
                assert data == {"name": "Test", "age": 30}
        finally:
            # Clean up
            import os
            os.unlink(yaml_file_path)
            os.unlink(json_file_path)

    def test_base_config_parser_not_implemented_methods(self):
        # Test that BaseConfigParser methods raise NotImplementedError
        class DummyParser(BaseConfigParser):
            def parse(self, f):
                return {}

        parser = DummyParser()

        with pytest.raises(NotImplementedError):
            parser.dump({}, io.StringIO())

        with pytest.raises(NotImplementedError):
            parser.parse_str("")

        with pytest.raises(NotImplementedError):
            parser.dump_str({})