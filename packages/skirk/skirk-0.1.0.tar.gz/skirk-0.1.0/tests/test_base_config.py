import os
import tempfile
from dataclasses import dataclass

from skirk.base_config import BaseConfig


@dataclass
class DemoConfig(BaseConfig):
    name: str
    age: int
    email: str = ""


class TestBaseConfig:
    def test_of_method_with_valid_data(self):
        # Test with valid data
        class DummySource:
            def parse(self):
                return {"name": "Test", "age": 30}

        config = DemoConfig.of(DummySource())
        assert config.name == "Test"
        assert config.age == 30
        assert config.email == ""

    def test_from_file_method(self):
        # Create a temporary config file
        with tempfile.NamedTemporaryFile(suffix=".json", mode="w", delete=False) as f:
            f.write('{"name": "Test", "age": 30}')
            temp_file_path = f.name

        try:
            # Test from_file method
            config = DemoConfig.from_file(temp_file_path)
            assert config.name == "Test"
            assert config.age == 30
        finally:
            # Clean up
            os.unlink(temp_file_path)

    def test_from_cli_method(self):
        # Test from_cli method
        args = ["--name", "Test", "--age", "30"]
        config = DemoConfig.from_cli(args=args)
        assert config.name == "Test"
        assert config.age == 30

    def test_dump_method(self):
        # Create a temporary file
        with tempfile.NamedTemporaryFile(suffix=".json", mode="w+", delete=False) as f:
            temp_file_path = f.name

        try:
            # Create a config and dump it
            config = DemoConfig(name="Test", age=30)
            config.dump(temp_file_path)

            # Verify the file content
            with open(temp_file_path) as f:
                content = f.read()
                assert "name" in content
                assert "Test" in content
                assert "age" in content
                assert "30" in content
        finally:
            # Clean up
            os.unlink(temp_file_path)