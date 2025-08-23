import re
from pathlib import Path

import pytest

from mcp_long_context_reader.context import LongTextContext
from mcp_long_context_reader.strategies.regex_search import RegexSearchStrategy


@pytest.fixture
def temp_content_path(tmp_path: Path) -> Path:
    """Fixture for a temporary path to save/load content."""
    return tmp_path / "test_content.txt"


class TestRegexSearchStrategy:
    """Tests for the RegexSearchStrategy."""

    def test_process_and_save_writes_content(self, temp_content_path: Path):
        """Tests that process_and_save writes the context content to a file."""
        strategy = RegexSearchStrategy()
        content = "Line 1: hello\nLine 2: world"
        context = LongTextContext(content)

        strategy.process_and_save(context, temp_content_path)

        assert temp_content_path.exists()
        assert temp_content_path.read_text(encoding="utf-8") == content

    def test_query_loads_and_searches(self, temp_content_path: Path):
        """Tests that query loads content and performs a search."""
        # Setup: Create dummy content file
        content = "The quick brown fox jumps over the lazy dog."
        temp_content_path.write_text(content, encoding="utf-8")

        strategy = RegexSearchStrategy()

        # Test a simple match
        result = strategy.query(r"brown fox", temp_content_path)
        assert "quick brown fox jumps" in result

        # Test no match
        result_none = strategy.query(r"nonexistent", temp_content_path)
        assert "No matches found" in result_none

    def test_query_with_context_window(self, temp_content_path: Path):
        """Tests the context window parameter."""
        content = "start_marker some text in the middle end_marker"
        temp_content_path.write_text(content)

        # Small context window
        strategy_small = RegexSearchStrategy(context_window=5)
        result_small = strategy_small.query(r"text", temp_content_path)
        assert "me text in" in result_small

        # Large context window (should capture everything)
        strategy_large = RegexSearchStrategy(context_window=50)
        result_large = strategy_large.query(r"text", temp_content_path)
        assert content in result_large
        assert "..." not in result_large  # No ellipsis if it's the full string

    def test_query_is_case_sensitive(self, temp_content_path: Path):
        """Tests the case sensitive parameter."""
        content = "Hello hello"
        temp_content_path.write_text(content)

        strategy = RegexSearchStrategy()

        # Default is case sensitive
        result_sensitive = strategy.query(r"hello", temp_content_path)
        # Should find only the lowercase "hello"
        matches_sensitive = re.findall(r"--- Result \d+/\d+ ---", result_sensitive)
        assert len(matches_sensitive) == 1

        # Case insensitive should find both "Hello" and "hello"
        result_insensitive = strategy.query(
            r"hello", temp_content_path, case_sensitive=False
        )
        matches_insensitive = re.findall(r"--- Result \d+/\d+ ---", result_insensitive)
        assert len(matches_insensitive) == 2

    def test_query_handles_invalid_regex(self, temp_content_path: Path):
        """Tests that the query method handles an invalid regex pattern gracefully."""
        content = "some content"
        temp_content_path.write_text(content)

        strategy = RegexSearchStrategy()
        # An unclosed bracket is an invalid regex
        result = strategy.query(r"[", temp_content_path)

        assert "Invalid regex pattern" in result

    def test_query_with_max_matches(self, temp_content_path: Path):
        """Tests that the query respects the max_matches parameter."""
        # Create content with more matches than the default limit
        content = "word " * 250
        temp_content_path.write_text(content)

        # 1. Test with a custom limit that is lower than the match count
        strategy_limited = RegexSearchStrategy(max_matches=5)
        result_limited = strategy_limited.query(r"word", temp_content_path)

        matches_found = re.findall(r"--- Result \d+/\d+ ---", result_limited)
        assert len(matches_found) == 5
        assert "Warning: Too many matches found (250)" in result_limited
        assert "Displaying the first 5 results." in result_limited
        assert "--- Result 1/250 ---" in result_limited
        assert "--- Result 5/250 ---" in result_limited

        # 2. Test with default limit, which is not exceeded here
        content_short = "word " * 150
        temp_content_path.write_text(content_short)
        strategy_default = RegexSearchStrategy()  # Default max_matches is 200
        result_default = strategy_default.query(r"word", temp_content_path)
        matches_default = re.findall(r"--- Result \d+/\d+ ---", result_default)
        assert len(matches_default) == 150
        assert "Warning" not in result_default

        # 3. Test with a limit equal to the number of matches
        strategy_exact = RegexSearchStrategy(max_matches=150)
        result_exact = strategy_exact.query(r"word", temp_content_path)
        matches_exact = re.findall(r"--- Result \d+/\d+ ---", result_exact)
        assert len(matches_exact) == 150
        assert "Warning" not in result_exact

    def test_query_match_truncation(self, temp_content_path: Path):
        """Tests that long matches are truncated and short ones are not."""
        # Case 1: Long match that should be truncated
        long_match_content = "b" * 1000
        content_long = f"prefix{'a' * 20}{long_match_content}{'c' * 20}suffix"
        temp_content_path.write_text(content_long)

        # max_match_display_len is smaller than len(long_match_content)
        strategy_long = RegexSearchStrategy(
            max_match_display_len=100, context_window=30
        )
        result_long = strategy_long.query(r"b+", temp_content_path)

        assert "[match truncated, original length: 1000]" in result_long
        # Check for the context and the start of the match
        assert "prefix" + "a" * 20 + "b" * 50 in result_long
        # Check for the context and the end of the match
        assert "b" * 50 + "c" * 20 + "suffix" in result_long
        # Check that the middle of the long match is not present
        assert "b" * 101 not in result_long

        # Case 2: Short match that should NOT be truncated
        short_match_content = "x" * 50
        content_short = f"prefix...{short_match_content}...suffix"
        temp_content_path.write_text(content_short)

        # max_match_display_len is larger than len(short_match_content)
        strategy_short = RegexSearchStrategy(
            max_match_display_len=100, context_window=20
        )
        result_short = strategy_short.query(r"x+", temp_content_path)

        assert "match truncated" not in result_short
        assert short_match_content in result_short
        assert "prefix..." in result_short
        assert "...suffix" in result_short
