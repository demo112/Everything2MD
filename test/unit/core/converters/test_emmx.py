"""
Tests for EmmxConverter - EMMX (mindmap) to Markdown conversion.
Requirements: 1.7
"""
import pytest
import json
import zipfile
from pathlib import Path
from unittest.mock import patch, MagicMock
from src.core.converters.emmx import EmmxConverter


@pytest.fixture
def converter():
    return EmmxConverter()


def create_emmx_file(path: Path, json_data: dict, json_filename: str = "doc/document.json"):
    """Helper to create a test emmx file (zip with JSON)"""
    with zipfile.ZipFile(path, 'w') as z:
        z.writestr(json_filename, json.dumps(json_data))


class TestEmmxConverter:
    """Tests for EMMX converter functionality"""

    def test_convert_basic_mindmap(self, converter, tmp_path):
        """Test basic mindmap conversion with doc/document.json structure"""
        input_file = tmp_path / "test.emmx"
        output_file = tmp_path / "test.md"

        # Create test data with models->map structure
        json_data = {
            "models": {
                "map": {
                    "text": "Root Topic",
                    "children": [
                        {"text": "Child 1"},
                        {"text": "Child 2", "children": [
                            {"text": "Grandchild"}
                        ]}
                    ]
                }
            }
        }
        create_emmx_file(input_file, json_data)

        result = converter.convert(input_file, output_file)

        assert result == output_file
        assert output_file.exists()
        content = output_file.read_text(encoding="utf-8")
        assert "Root Topic" in content
        assert "Child 1" in content
        assert "Child 2" in content
        assert "Grandchild" in content

    def test_convert_mindmap_json_structure(self, converter, tmp_path):
        """Test mindmap.json structure"""
        input_file = tmp_path / "test.emmx"
        output_file = tmp_path / "test.md"

        json_data = {
            "root": {
                "text": "Main Topic",
                "children": [
                    {"text": "Branch A"},
                    {"text": "Branch B"}
                ]
            }
        }
        create_emmx_file(input_file, json_data, "mindmap.json")

        result = converter.convert(input_file, output_file)

        assert result == output_file
        content = output_file.read_text(encoding="utf-8")
        assert "Main Topic" in content
        assert "Branch A" in content
        assert "Branch B" in content

    def test_convert_topic_structure(self, converter, tmp_path):
        """Test topic-based structure (MindMaster style)"""
        input_file = tmp_path / "test.emmx"
        output_file = tmp_path / "test.md"

        json_data = {
            "topic": {
                "text": "Central Idea",
                "topics": [
                    {"text": "Sub Topic 1"},
                    {"text": "Sub Topic 2"}
                ]
            }
        }
        create_emmx_file(input_file, json_data)

        result = converter.convert(input_file, output_file)

        assert result == output_file
        content = output_file.read_text(encoding="utf-8")
        assert "Central Idea" in content
        assert "Sub Topic 1" in content

    def test_convert_direct_children_structure(self, converter, tmp_path):
        """Test direct children structure"""
        input_file = tmp_path / "test.emmx"
        output_file = tmp_path / "test.md"

        json_data = {
            "text": "Direct Root",
            "children": [
                {"text": "Item 1"},
                {"text": "Item 2"}
            ]
        }
        create_emmx_file(input_file, json_data)

        result = converter.convert(input_file, output_file)

        assert result == output_file
        content = output_file.read_text(encoding="utf-8")
        assert "Direct Root" in content
        assert "Item 1" in content

    def test_convert_rich_text_content(self, converter, tmp_path):
        """Test rich text content extraction"""
        input_file = tmp_path / "test.emmx"
        output_file = tmp_path / "test.md"

        json_data = {
            "models": {
                "map": {
                    "text": {"content": "Rich Text Node"},
                    "children": []
                }
            }
        }
        create_emmx_file(input_file, json_data)

        result = converter.convert(input_file, output_file)

        content = output_file.read_text(encoding="utf-8")
        assert "Rich Text Node" in content

    def test_convert_title_field(self, converter, tmp_path):
        """Test title field extraction"""
        input_file = tmp_path / "test.emmx"
        output_file = tmp_path / "test.md"

        json_data = {
            "models": {
                "map": {
                    "title": "Title Based Node",
                    "children": []
                }
            }
        }
        create_emmx_file(input_file, json_data)

        result = converter.convert(input_file, output_file)

        content = output_file.read_text(encoding="utf-8")
        assert "Title Based Node" in content

    def test_convert_invalid_zip(self, converter, tmp_path):
        """Test handling of invalid zip file"""
        input_file = tmp_path / "invalid.emmx"
        output_file = tmp_path / "test.md"

        # Create invalid zip
        input_file.write_text("not a zip file")

        with pytest.raises(Exception):
            converter.convert(input_file, output_file)

    def test_convert_missing_json(self, converter, tmp_path):
        """Test handling of emmx without expected JSON"""
        input_file = tmp_path / "empty.emmx"
        output_file = tmp_path / "test.md"

        # Create zip without expected JSON files
        with zipfile.ZipFile(input_file, 'w') as z:
            z.writestr("other.txt", "some content")

        with pytest.raises(Exception):
            converter.convert(input_file, output_file)

    def test_convert_unrecognized_structure(self, converter, tmp_path):
        """Test handling of unrecognized JSON structure"""
        input_file = tmp_path / "unknown.emmx"
        output_file = tmp_path / "test.md"

        json_data = {
            "unknown_key": "value",
            "another_key": []
        }
        create_emmx_file(input_file, json_data)

        with pytest.raises(Exception):
            converter.convert(input_file, output_file)

    def test_convert_creates_output_directory(self, converter, tmp_path):
        """Test that output directory is created if it doesn't exist"""
        input_file = tmp_path / "test.emmx"
        output_file = tmp_path / "subdir" / "nested" / "test.md"

        json_data = {
            "models": {
                "map": {
                    "text": "Test",
                    "children": []
                }
            }
        }
        create_emmx_file(input_file, json_data)

        result = converter.convert(input_file, output_file)

        assert result == output_file
        assert output_file.exists()

    def test_convert_nested_topic_structure(self, converter, tmp_path):
        """Test nested topic structure"""
        input_file = tmp_path / "test.emmx"
        output_file = tmp_path / "test.md"

        json_data = {
            "models": {
                "map": {
                    "topic": {
                        "text": "Nested Topic Root",
                        "children": [
                            {"text": "Nested Child"}
                        ]
                    }
                }
            }
        }
        create_emmx_file(input_file, json_data)

        result = converter.convert(input_file, output_file)

        content = output_file.read_text(encoding="utf-8")
        assert "Nested Topic Root" in content
        assert "Nested Child" in content

    def test_markdown_list_format(self, converter, tmp_path):
        """Test that output is formatted as markdown list"""
        input_file = tmp_path / "test.emmx"
        output_file = tmp_path / "test.md"

        json_data = {
            "models": {
                "map": {
                    "text": "Root",
                    "children": [
                        {"text": "Level 1", "children": [
                            {"text": "Level 2"}
                        ]}
                    ]
                }
            }
        }
        create_emmx_file(input_file, json_data)

        converter.convert(input_file, output_file)

        content = output_file.read_text(encoding="utf-8")
        # Check markdown list format
        assert "- Root" in content
        assert "  - Level 1" in content
        assert "    - Level 2" in content
