import pytest
from pathlib import Path

from mcp_long_context_reader.context import LongTextContext

RESOURCES_DIR = Path(__file__).parent.parent / "resources"


class TestLongTextContext:
    """Tests for the LongTextContext class."""

    def test_from_file_loads_content(self):
        """Tests that LongTextContext can be created from a file path."""
        context_file = RESOURCES_DIR / "longbench0_context.txt"
        assert context_file.exists(), f"Test resource file not found at {context_file}"

        context = LongTextContext.from_file(context_file)
        assert isinstance(context.content, str)
        assert len(context.content) > 100000  # Check for substantial content

        # Verify the beginning of the content matches the file
        with open(context_file, "r", encoding="utf-8") as f:
            expected_start = f.read(200)
        assert context.content.startswith(expected_start)

    def test_from_string_loads_content(self):
        """Tests that LongTextContext can be created from a string."""
        test_string = "This is a simple test string.\nIt has two lines."
        context = LongTextContext.from_string(test_string)
        assert isinstance(context.content, str)
        assert context.content == test_string

    def test_from_empty_string(self):
        """Tests creating context from an empty string."""
        context = LongTextContext.from_string("")
        assert context.content == ""

    def test_from_file_raises_error_for_nonexistent_file(self):
        """Tests that a FileNotFoundError is raised for a nonexistent file."""
        non_existent_file = Path("this/path/absolutely/does/not/exist.txt")
        with pytest.raises(FileNotFoundError):
            LongTextContext.from_file(non_existent_file)
