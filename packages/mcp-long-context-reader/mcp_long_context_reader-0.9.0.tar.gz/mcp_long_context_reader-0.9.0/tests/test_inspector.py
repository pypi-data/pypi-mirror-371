import pytest
from pathlib import Path

# This import will fail initially, which is expected in TDD
from mcp_long_context_reader.inspector import FileInspector


class TestFileInspector:
    @pytest.fixture
    def inspector(self):
        """Returns a FileInspector instance with a small char_limit for testing."""
        return FileInspector(char_limit=100)

    def test_glance_large_file(self, inspector, tmp_path: Path):
        """Tests glancing at a file larger than the character limit."""
        content = "This is the first line.\n" + "a" * 200
        total_lines = 2
        p = tmp_path / "large_file.txt"
        p.write_text(content, encoding="utf-8")

        result = inspector.glance(p)

        snippet = content[:100]
        snippet_lines = snippet.count("\n") + 1
        char_count = len(snippet)

        expected_start = (
            f"Showing the first {char_count} characters (~{snippet_lines} lines) "
            f"of {total_lines} total lines."
        )
        assert result.startswith(expected_start)
        assert content[:100] in result
        assert "a" * 200 not in result

    def test_glance_small_file(self, inspector, tmp_path: Path):
        """Tests glancing at a file smaller than the character limit."""
        content = "Hello world.\nThis is a small file."
        p = tmp_path / "small_file.txt"
        p.write_text(content, encoding="utf-8")

        result = inspector.glance(p)

        total_lines = 2
        snippet_lines = 2
        char_count = len(content)

        expected_start = (
            f"Showing the first {char_count} characters (~{snippet_lines} lines) "
            f"of {total_lines} total lines."
        )
        assert result.startswith(expected_start)
        assert content in result

    def test_glance_empty_file(self, inspector, tmp_path: Path):
        """Tests glancing at an empty file."""
        p = tmp_path / "empty_file.txt"
        p.touch()

        result = inspector.glance(p)

        expected = (
            "Showing the first 0 characters (~0 lines) of 0 total lines.\n"
            "---\n"
            "(Empty file)"
        )
        assert result == expected

    def test_glance_single_line_file(self, inspector, tmp_path: Path):
        """Tests a file with a single line and no newline character."""
        content = "This is a single line file."
        p = tmp_path / "single_line.txt"
        p.write_text(content, encoding="utf-8")

        result = inspector.glance(p)

        total_lines = 1
        snippet_lines = 1
        char_count = len(content)

        expected_start = (
            f"Showing the first {char_count} characters (~{snippet_lines} lines) "
            f"of {total_lines} total lines."
        )
        assert result.startswith(expected_start)
        assert content in result
