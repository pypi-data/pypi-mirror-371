from __future__ import annotations
from pathlib import Path


class LongTextContext:
    """A container for holding and loading long text contexts."""

    def __init__(self, content: str):
        """
        Initializes the context with text content.

        It's recommended to use the `from_file` or `from_string`
        classmethods for instantiation.
        """
        self.content = content

    @classmethod
    def from_file(cls, file_path: str | Path) -> LongTextContext:
        """
        Creates a LongTextContext instance by reading a text file.

        Args:
            file_path: The path to the text file.

        Returns:
            An instance of LongTextContext.

        Raises:
            FileNotFoundError: If the file does not exist.
        """
        path = Path(file_path)
        content = path.read_text(encoding="utf-8")
        return cls(content)

    @classmethod
    def from_string(cls, text: str) -> LongTextContext:
        """
        Creates a LongTextContext instance from a string.

        Args:
            text: The string content.

        Returns:
            An instance of LongTextContext.
        """
        return cls(text)
