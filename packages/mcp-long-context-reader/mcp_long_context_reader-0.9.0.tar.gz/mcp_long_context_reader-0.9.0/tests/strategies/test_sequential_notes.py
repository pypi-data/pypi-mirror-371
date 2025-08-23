import pickle
from pathlib import Path
from unittest.mock import MagicMock

import pytest
from langchain_core.language_models.chat_models import BaseChatModel

from mcp_long_context_reader.context import LongTextContext
from mcp_long_context_reader.strategies.sequential_notes import SequentialNotesStrategy
from mcp_long_context_reader.utils import TimeoutError


@pytest.fixture
def mock_llm() -> MagicMock:
    """Fixture for a mock LLM."""
    mock = MagicMock(spec=BaseChatModel)
    # Simulate the LLM's invoke method returning a message-like object
    mock.invoke.return_value.content = "Updated notes."
    return mock


@pytest.fixture
def temp_cache_path(tmp_path: Path) -> Path:
    """Fixture for a temporary path to save/load chunks."""
    return tmp_path / "test_chunks.pkl"


class TestSequentialNotesStrategy:
    def test_process_and_save_chunks(self, mock_llm: MagicMock, temp_cache_path: Path):
        """Tests that process_and_save correctly chunks and pickles the text."""
        strategy = SequentialNotesStrategy(
            llm=mock_llm, chunk_size=200, chunk_overlap=0
        )
        content = "a" * 500
        context = LongTextContext(content)

        strategy.process_and_save(context, temp_cache_path)

        assert temp_cache_path.exists()
        with open(temp_cache_path, "rb") as f:
            chunks = pickle.load(f)

        assert isinstance(chunks, list)
        assert len(chunks) > 1
        assert "".join(chunks) == content

    def test_process_and_save_chunks_with_overlap(
        self, mock_llm: MagicMock, temp_cache_path: Path
    ):
        """Tests that process_and_save correctly handles chunk overlap."""
        overlap = 20
        strategy = SequentialNotesStrategy(
            llm=mock_llm, chunk_size=200, chunk_overlap=overlap
        )
        content = "a" * 500
        context = LongTextContext(content)

        strategy.process_and_save(context, temp_cache_path)

        with open(temp_cache_path, "rb") as f:
            chunks = pickle.load(f)

        assert len(chunks) > 1
        # The end of the first chunk should match the start of the second chunk
        assert chunks[0][-overlap:] == chunks[1][:overlap]

    def test_query_iterates_and_returns_notes(
        self, mock_llm: MagicMock, temp_cache_path: Path
    ):
        """Tests the full query flow using saved chunks and a mock LLM."""
        # Setup: Create dummy chunk file
        dummy_chunks = ["First part.", "Second part."]
        with open(temp_cache_path, "wb") as f:
            pickle.dump(dummy_chunks, f)

        # Pass the mock LLM via params
        strategy = SequentialNotesStrategy(
            llm=mock_llm, chunk_size=200, chunk_overlap=10
        )

        final_notes = strategy.query("What happened?", temp_cache_path)

        # Verify LLM was called for each chunk
        assert mock_llm.invoke.call_count == len(dummy_chunks)

        # Verify the final notes are returned
        assert final_notes == "Updated notes."

        # Verify the prompt was constructed correctly on the last call
        last_call_args, _ = mock_llm.invoke.call_args
        last_prompt = last_call_args[0]
        assert "What happened?" in str(last_prompt)
        assert "Second part." in str(last_prompt)
        # The notes passed to the last call would be the result of the first call
        assert "Updated notes." in str(last_prompt)

    def test_init_raises_error_on_invalid_params(self, mock_llm: MagicMock):
        """Tests that __init__ raises ValueError for invalid chunk sizes."""
        with pytest.raises(ValueError, match="chunk_size must be at least 200"):
            SequentialNotesStrategy(llm=mock_llm, chunk_size=100)

        with pytest.raises(ValueError, match="chunk_overlap must be smaller"):
            SequentialNotesStrategy(llm=mock_llm, chunk_size=200, chunk_overlap=200)

    def test_init_raises_error_on_invalid_timeout(self, mock_llm: MagicMock):
        """Tests that __init__ raises ValueError for invalid timeout values."""
        with pytest.raises(ValueError, match="chunk_timeout must be positive"):
            SequentialNotesStrategy(llm=mock_llm, chunk_timeout=0)

        with pytest.raises(ValueError, match="chunk_timeout must be positive"):
            SequentialNotesStrategy(llm=mock_llm, chunk_timeout=-5)

    def test_init_raises_error_without_llm(self):
        """Tests that __init__ raises KeyError if llm is not provided."""
        with pytest.raises(KeyError, match="An 'llm' instance must be provided"):
            SequentialNotesStrategy()

    def test_timeout_default_value(self, mock_llm: MagicMock):
        """Tests that chunk_timeout has a default value of 60 seconds."""
        strategy = SequentialNotesStrategy(llm=mock_llm)
        assert strategy.chunk_timeout == 60

    def test_timeout_custom_value(self, mock_llm: MagicMock):
        """Tests that chunk_timeout can be set to a custom value."""
        strategy = SequentialNotesStrategy(llm=mock_llm, chunk_timeout=30)
        assert strategy.chunk_timeout == 30

    def test_query_handles_llm_error_and_skips_chunk(
        self, mock_llm: MagicMock, temp_cache_path: Path
    ):
        """Tests that the query method skips a chunk if the LLM call fails."""
        # Setup: Create dummy chunk file
        dummy_chunks = ["First part.", "Problematic part.", "Third part."]
        with open(temp_cache_path, "wb") as f:
            pickle.dump(dummy_chunks, f)

        # Configure mock to fail on the second call
        response1 = MagicMock()
        response1.content = "Notes from first part."
        response3 = MagicMock()
        response3.content = "Notes from first and third parts."
        mock_llm.invoke.side_effect = [
            response1,
            Exception("Simulated API error"),
            response3,
        ]

        strategy = SequentialNotesStrategy(
            llm=mock_llm, chunk_size=200, chunk_overlap=10
        )

        final_notes = strategy.query("Test query", temp_cache_path)

        # Verify LLM was called for all three chunks
        assert mock_llm.invoke.call_count == len(dummy_chunks)

        # Verify that the final notes are from the last successful update
        assert final_notes == "Notes from first and third parts."

        # Check that the note from the first call was passed to the third call
        last_call_args, _ = mock_llm.invoke.call_args
        last_prompt = str(last_call_args[0])
        assert "Notes from first part." in last_prompt
        assert "Third part." in last_prompt

    def test_query_timeout_handling(self, mock_llm: MagicMock, temp_cache_path: Path):
        """Tests that the query method stops and returns a message on TimeoutError."""
        # Setup: Create dummy chunk file
        dummy_chunks = ["First part.", "Second part.", "Third part."]
        with open(temp_cache_path, "wb") as f:
            pickle.dump(dummy_chunks, f)

        # Mock LLM to simulate a success then a timeout
        response1 = MagicMock()
        response1.content = "Notes from first part."
        mock_llm.invoke.side_effect = [
            response1,
            TimeoutError("Simulated timeout"),
        ]

        # Use a very short timeout for testing (1 second)
        strategy = SequentialNotesStrategy(llm=mock_llm, chunk_timeout=1)

        final_output = strategy.query("Test query", temp_cache_path)

        # Verify LLM was called up to the point of failure
        assert mock_llm.invoke.call_count == 2

        # Verify the returned message
        assert "Sequential notes processing timed out" in final_output
        assert f"Processed 1 out of {len(dummy_chunks)} chunks" in final_output
        assert "Note at timeout:\n\nNotes from first part." in final_output
