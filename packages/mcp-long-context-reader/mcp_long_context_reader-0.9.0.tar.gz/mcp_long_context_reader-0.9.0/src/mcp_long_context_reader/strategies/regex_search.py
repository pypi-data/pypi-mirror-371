import re
from pathlib import Path
from typing import List

from mcp_long_context_reader.context import LongTextContext
from mcp_long_context_reader.strategies.base import SearchStrategy


class RegexSearchStrategy(SearchStrategy):
    """A search strategy that uses regular expressions."""

    def __init__(self, **strategy_params):
        super().__init__(**strategy_params)
        self.context_window = self.params.get("context_window", 50)
        self.max_matches = self.params.get("max_matches", 200)
        self.max_match_display_len = self.params.get("max_match_display_len", 500)

        if self.context_window < 0:
            raise ValueError("context_window cannot be negative.")
        if self.max_matches <= 0:
            raise ValueError("max_matches must be positive.")
        if self.max_match_display_len <= 0:
            raise ValueError("max_match_display_len must be positive.")

    def process_and_save(self, context: LongTextContext, save_path: Path):
        """Saves the raw context content to the cache path."""
        with open(save_path, "w", encoding="utf-8") as f:
            f.write(context.content)

    def query(self, query: str, load_path: Path, case_sensitive: bool = True) -> str:
        """
        Loads the raw content and finds all occurrences of a regex pattern.
        """
        if not load_path.exists():
            return "Error: Cached content not found."

        with open(load_path, "r", encoding="utf-8") as f:
            content = f.read()

        flags = 0 if case_sensitive else re.IGNORECASE
        try:
            matches = list(re.finditer(query, content, flags))
        except re.error as e:
            return f"Invalid regex pattern: {e}"

        if not matches:
            return "No matches found for the given regex pattern."

        total_matches = len(matches)
        if total_matches > self.max_matches:
            display_matches = matches[: self.max_matches]
        else:
            display_matches = matches

        results: List[str] = []
        for i, match in enumerate(display_matches):
            start, end = match.span()
            matched_text = content[start:end]
            match_len = len(matched_text)

            display_match_text = matched_text
            if match_len > self.max_match_display_len:
                head_len = (self.max_match_display_len + 1) // 2
                tail_len = self.max_match_display_len // 2
                head = matched_text[:head_len]
                tail = matched_text[-tail_len:]
                truncation_message = (
                    f"... [match truncated, original length: {match_len}] ..."
                )
                display_match_text = head + truncation_message + tail

            window_start = max(0, start - self.context_window)
            window_end = min(len(content), end + self.context_window)

            context_before = content[window_start:start]
            context_after = content[end:window_end]

            snippet = context_before + display_match_text + context_after
            prefix = "..." if window_start > 0 else ""
            suffix = "..." if window_end < len(content) else ""

            results.append(
                f"--- Result {i + 1}/{total_matches} ---\n{prefix}{snippet}{suffix}"
            )

        output = "\n\n".join(results)

        if total_matches > self.max_matches:
            output += (
                f"\n\n---"
                f"\nWarning: Too many matches found ({total_matches}). "
                f"Displaying the first {self.max_matches} results."
                f"\n---"
            )

        return output
