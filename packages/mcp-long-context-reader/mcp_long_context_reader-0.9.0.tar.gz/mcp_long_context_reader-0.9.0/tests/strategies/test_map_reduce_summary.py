import pickle
from pathlib import Path
from unittest.mock import MagicMock
import time

import pytest
from langchain_core.language_models.chat_models import BaseChatModel

from mcp_long_context_reader.context import LongTextContext
from mcp_long_context_reader.strategies.map_reduce_summary import (
    MapReduceSummaryStrategy,
)


@pytest.fixture
def temp_cache_path(tmp_path: Path) -> Path:
    """Fixture for a temporary path to save/load chunks."""
    return tmp_path / "test_chunks_mapreduce.pkl"


@pytest.fixture
def mock_llm() -> MagicMock:
    """Fixture for a mock LLM."""
    mock = MagicMock(spec=BaseChatModel)
    # Add get_num_tokens method to return a reasonable number for token counting
    mock.get_num_tokens.return_value = 100
    return mock


class TestMapReduceSummaryStrategy:
    def test_process_and_save_chunks(self, mock_llm: MagicMock, temp_cache_path: Path):
        """Tests that process_and_save correctly chunks and pickles the text."""
        strategy = MapReduceSummaryStrategy(
            llm=mock_llm, chunk_size=500, chunk_overlap=0
        )
        # Make content long enough to be chunked
        content = "a" * 1000
        context = LongTextContext(content)

        strategy.process_and_save(context, temp_cache_path)

        assert temp_cache_path.exists()
        with open(temp_cache_path, "rb") as f:
            chunks = pickle.load(f)

        assert isinstance(chunks, list)
        assert len(chunks) > 1
        assert "".join(chunks) == content

    def test_query_filters_and_reduces_successfully(
        self,
        mock_llm: MagicMock,
        temp_cache_path: Path,
    ):
        """
        Tests the full query process by mocking the LLM's responses, ensuring
        that irrelevant chunks are filtered out before the reduce step.
        """
        # Setup: Create dummy chunk file
        dummy_chunks = [
            "This part has relevant info.",
            "This part is irrelevant.",
            "This part also has relevant info.",
        ]
        with open(temp_cache_path, "wb") as f:
            pickle.dump(dummy_chunks, f)

        # Mock LLM responses for both map and reduce steps
        # Map step responses for each chunk
        map_results = [
            "Summary of first relevant part.",
            "This part does not contain any information.",
            "Summary of second relevant part.",
        ]

        # For reduce step
        reduce_result = "This is the final synthesized summary."

        # The map step now uses batch, and the reduce step uses invoke
        mock_llm.batch.return_value = map_results
        mock_llm.invoke.return_value = reduce_result

        # Execution
        strategy = MapReduceSummaryStrategy(llm=mock_llm, chunk_size=1000)
        summary = strategy.query("What is the relevant info?", temp_cache_path)

        # Verification
        # 1. Verify LLM was called correctly (1 map batch call + 1 reduce invoke call)
        assert mock_llm.batch.call_count == 1
        assert mock_llm.invoke.call_count == 1

        # 2. Inspect the content passed to the reduce step (the last call)
        # The reduce chain stuffs the documents into a context string.
        # We need to check that this context contains the relevant summaries
        # and excludes the irrelevant one.
        final_call_args = mock_llm.invoke.call_args
        reduce_input_prompt = final_call_args[0][0].text

        assert "Summary of first relevant part." in reduce_input_prompt
        assert "Summary of second relevant part." in reduce_input_prompt
        assert "This part does not contain any information." not in reduce_input_prompt

        # 3. Check final summary is correct
        assert summary == reduce_result

    def test_query_returns_early_if_all_chunks_are_filtered(
        self, mock_llm: MagicMock, temp_cache_path: Path
    ):
        """
        Tests that if all chunks are filtered out, the function returns an
        appropriate message without calling the reduce chain's LLM.
        """
        # Setup
        dummy_chunks = ["irrelevant chunk 1", "irrelevant chunk 2"]
        with open(temp_cache_path, "wb") as f:
            pickle.dump(dummy_chunks, f)

        # Mock Map response to return only "no info" messages
        map_results = [
            "This text does not contain any information.",
            "This part of the document does not contain any information.",
        ]

        mock_llm.batch.return_value = map_results

        # Execution
        strategy = MapReduceSummaryStrategy(llm=mock_llm)
        summary = strategy.query("A question", temp_cache_path)

        # Verification
        # batch should be called for map step only (no reduce step)
        assert mock_llm.batch.call_count == 1
        assert mock_llm.invoke.call_count == 0
        assert (
            summary
            == "The document does not contain information to answer the question."
        )

    def test_process_and_save_chunks_with_overlap(
        self, mock_llm: MagicMock, temp_cache_path: Path
    ):
        """Tests that process_and_save correctly handles chunk overlap."""
        overlap = 50
        strategy = MapReduceSummaryStrategy(
            llm=mock_llm, chunk_size=500, chunk_overlap=overlap
        )
        content = "abc" * 1000
        context = LongTextContext(content)

        strategy.process_and_save(context, temp_cache_path)

        with open(temp_cache_path, "rb") as f:
            chunks = pickle.load(f)

        assert len(chunks) > 1
        # The end of the first chunk should match the start of the second chunk
        assert chunks[0][-overlap:] == chunks[1][:overlap]

    def test_init_raises_error_on_invalid_params(self, mock_llm: MagicMock):
        """Tests that __init__ raises ValueError for invalid chunk sizes."""
        with pytest.raises(ValueError, match="chunk_size must be at least 500"):
            MapReduceSummaryStrategy(llm=mock_llm, chunk_size=100)

        with pytest.raises(ValueError, match="chunk_overlap must be smaller"):
            MapReduceSummaryStrategy(llm=mock_llm, chunk_size=500, chunk_overlap=500)

    def test_init_raises_error_without_llm(self):
        """Tests that __init__ raises KeyError if llm is not provided."""
        with pytest.raises(KeyError, match="An 'llm' instance must be provided"):
            MapReduceSummaryStrategy()

    def test_query_with_no_chunks_returns_empty_message(
        self, mock_llm: MagicMock, temp_cache_path: Path
    ):
        """Tests that query returns an appropriate message if the chunk file is empty."""
        # Setup: Create an empty chunk file
        dummy_chunks = []
        with open(temp_cache_path, "wb") as f:
            pickle.dump(dummy_chunks, f)

        # Execution
        strategy = MapReduceSummaryStrategy(llm=mock_llm)
        summary = strategy.query("A question", temp_cache_path)

        # Verification
        assert mock_llm.batch.call_count == 0
        assert mock_llm.invoke.call_count == 0
        assert summary == "The document is empty."

    def test_query_with_nonexistent_cache_file(self, mock_llm: MagicMock):
        """Tests that query returns an error if the cache file does not exist."""
        strategy = MapReduceSummaryStrategy(llm=mock_llm)
        non_existent_path = Path("non_existent_file.txt")
        summary = strategy.query("A question", non_existent_path)
        assert summary == "Error: Cached chunks not found."

    def test_query_times_out_correctly(
        self, mock_llm: MagicMock, temp_cache_path: Path
    ):
        """
        Tests that the query method correctly times out if processing takes too long.
        """
        # Setup: Create dummy chunk file
        dummy_chunks = ["chunk 1", "chunk 2"]
        with open(temp_cache_path, "wb") as f:
            pickle.dump(dummy_chunks, f)

        # Configure strategy with a very short timeout
        timeout_duration = 1
        strategy = MapReduceSummaryStrategy(
            llm=mock_llm, query_timeout=timeout_duration
        )

        # Mock the batch call to take longer than the timeout
        def long_running_batch(*args, **kwargs):
            time.sleep(timeout_duration + 0.1)
            return ["result1", "result2"]  # This won't be reached

        mock_llm.batch.side_effect = long_running_batch

        # Execution
        summary = strategy.query("A question", temp_cache_path)

        # Verification
        assert mock_llm.batch.call_count == 1
        assert (
            summary
            == f"Map-reduce summary processing timed out after {timeout_duration} seconds."
        )
