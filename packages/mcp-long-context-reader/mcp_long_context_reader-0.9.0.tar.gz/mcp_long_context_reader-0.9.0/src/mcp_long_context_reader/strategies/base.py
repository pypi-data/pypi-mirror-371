from abc import ABC, abstractmethod
from pathlib import Path

from mcp_long_context_reader.context import LongTextContext


class SearchStrategy(ABC):
    """
    Abstract base class for all context search strategies.
    Designed for a stateless, load/save workflow.
    """

    def __init__(self, **strategy_params):
        """
        Lightweight initializer that sets strategy-specific parameters.

        Args:
            **strategy_params: A dictionary of parameters for the strategy,
                               e.g., {"chunk_size": 512}.
        """
        self.params = strategy_params

    @abstractmethod
    def process_and_save(self, context: LongTextContext, save_path: Path):
        """
        Executes the expensive, one-time pre-processing and serializes
        the resulting state to the given path.

        Args:
            context: The LongTextContext object containing the source text.
            save_path: The file path to save the processed artifact to.
        """
        pass

    @abstractmethod
    def query(self, query: str, load_path: Path) -> str:
        """
        Deserializes the state from the given path and executes the fast
        query action.

        Args:
            query: The search query (e.g., a regex pattern, a question).
            load_path: The file path to load the processed artifact from.

        Returns:
            A string containing the formatted search results (evidence).
        """
        pass
