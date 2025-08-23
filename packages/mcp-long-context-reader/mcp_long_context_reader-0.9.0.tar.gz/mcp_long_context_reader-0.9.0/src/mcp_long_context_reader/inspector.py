from pathlib import Path


class FileInspector:
    """Provides methods to inspect files."""

    def __init__(self, char_limit: int = 5000):
        """
        Initializes the FileInspector.

        Args:
            char_limit (int): The maximum number of characters to show in a glance.
        """
        if char_limit <= 0:
            raise ValueError("char_limit must be positive.")
        self.char_limit = char_limit

    def glance(self, file_path: Path) -> str:
        """
        Provides a quick overview of a file, showing the first N characters
        and some metadata.

        Args:
            file_path (Path): The path to the file to inspect.

        Returns:
            A formatted string containing a snippet of the file and metadata.
        """
        if not file_path.exists() or file_path.stat().st_size == 0:
            return (
                "Showing the first 0 characters (~0 lines) of 0 total lines.\n"
                "---\n"
                "(Empty file)"
            )

        # Read total lines without loading the whole file into memory
        with file_path.open("r", encoding="utf-8", errors="ignore") as f:
            total_lines = sum(1 for _ in f)

        with file_path.open("r", encoding="utf-8", errors="ignore") as f:
            snippet = f.read(self.char_limit)

        char_count = len(snippet)

        # The tilde `~` in the output indicates this is an approximation.
        # This logic is simple and sufficient for the defined test cases.
        snippet_lines = snippet.count("\n") + 1 if snippet else 0

        header = (
            f"Showing the first {char_count} characters (~{snippet_lines} lines) "
            f"of {total_lines} total lines."
        )
        return f"{header}\n---\n{snippet}"
