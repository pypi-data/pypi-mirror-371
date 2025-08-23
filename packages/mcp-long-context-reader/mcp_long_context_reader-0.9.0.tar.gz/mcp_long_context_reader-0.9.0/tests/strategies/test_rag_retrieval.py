from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest
from langchain_core.embeddings import Embeddings

from mcp_long_context_reader.context import LongTextContext
from mcp_long_context_reader.strategies.rag_retrieval import RAGRetrievalStrategy


# Mock the Document class from LangChain, as it's a simple data container
class Document:
    def __init__(self, page_content, metadata=None):
        self.page_content = page_content
        self.metadata = metadata or {}


@pytest.fixture
def rag_context() -> LongTextContext:
    """Provides a simple context for RAG strategy testing."""
    text = (
        "The first document is about programming in Python. "
        "The second document is about machine learning. "
        "The third document discusses the Python programming language."
    )
    return LongTextContext.from_string(text)


class TestRAGRetrievalStrategy:
    """Tests for the RAGRetrievalStrategy."""

    @patch(
        "mcp_long_context_reader.strategies.rag_retrieval.RecursiveCharacterTextSplitter"
    )
    @patch("mcp_long_context_reader.strategies.rag_retrieval.FAISS")
    def test_rag_retrieval_flow(
        self,
        MockFAISS,
        MockTextSplitter,
        rag_context,
        tmp_path: Path,
    ):
        """
        Tests the end-to-end flow of process_and_save -> query using mocks.
        """
        # 1. Setup Mocks
        mock_splitter_instance = MockTextSplitter.return_value
        mock_splitter_instance.split_text.return_value = ["chunk1", "chunk2"]

        mock_faiss_instance = MagicMock()
        MockFAISS.from_texts.return_value = mock_faiss_instance
        MockFAISS.load_local.return_value = mock_faiss_instance

        mock_retriever = mock_faiss_instance.as_retriever.return_value
        mock_retriever.get_relevant_documents.return_value = [
            Document(page_content="chunk1")
        ]
        save_path = tmp_path / "test_index"
        mock_embeddings = MagicMock(spec=Embeddings)

        # 2. Instantiate with valid parameters, injecting the mock embeddings
        strategy = RAGRetrievalStrategy(
            embeddings=mock_embeddings, chunk_size=100, chunk_overlap=10, top_k=1
        )

        # 3. Test process_and_save
        strategy.process_and_save(rag_context, save_path)
        MockTextSplitter.assert_called_with(
            chunk_size=100, chunk_overlap=10, length_function=len
        )
        # Assert that the injected embeddings were used
        MockFAISS.from_texts.assert_called_with(
            texts=["chunk1", "chunk2"], embedding=mock_embeddings
        )
        mock_faiss_instance.save_local.assert_called_once_with(str(save_path))

        # Simulate that save_local created the directory and files
        save_path.mkdir()
        (save_path / "index.faiss").touch()

        # 4. Test query
        result = strategy.query("some query", save_path)
        # Assert that the injected embeddings were used
        MockFAISS.load_local.assert_called_with(
            str(save_path), mock_embeddings, allow_dangerous_deserialization=True
        )
        mock_retriever.get_relevant_documents.assert_called_once_with("some query")
        assert "Retrieved Document 1/1" in result
        assert "chunk1" in result

    @patch("mcp_long_context_reader.strategies.rag_retrieval.FAISS")
    def test_process_and_save_creates_and_saves_index(self, MockFAISS, tmp_path: Path):
        """
        Tests that `process_and_save` chunks text, creates a FAISS index,
        and saves it to the specified path.
        """
        # Setup Mocks and a longer text
        mock_vectorstore = MockFAISS.from_texts.return_value
        content = (
            "This is a long text for testing purposes. It must be split into "
            "multiple chunks. The validation requires a chunk size of at least "
            "fifty characters, so we make this text long enough to test that."
        )
        context = LongTextContext(content)
        save_path = tmp_path / "faiss_index"
        mock_embeddings = MagicMock(spec=Embeddings)

        # Instantiate with valid chunk size and execute
        strategy = RAGRetrievalStrategy(
            embeddings=mock_embeddings, chunk_size=60, chunk_overlap=10
        )
        strategy.process_and_save(context, save_path)

        # Assertions
        # Check that the text was chunked and passed to FAISS with the embeddings
        MockFAISS.from_texts.assert_called_once()
        call_args, call_kwargs = MockFAISS.from_texts.call_args
        assert "texts" in call_kwargs
        assert len(call_kwargs["texts"]) > 1  # Check that splitting occurred
        assert content.startswith(
            call_kwargs["texts"][0]
        )  # First chunk is start of content
        assert call_kwargs["embedding"] == mock_embeddings

        # Check that the save method was called on the vectorstore instance
        mock_vectorstore.save_local.assert_called_once_with(str(save_path))

    @patch("mcp_long_context_reader.strategies.rag_retrieval.FAISS")
    def test_query_loads_index_and_retrieves(self, MockFAISS, tmp_path: Path):
        """
        Tests that `query` loads a FAISS index and uses it to retrieve documents.
        """
        # Setup Mocks
        mock_vectorstore = MockFAISS.load_local.return_value
        mock_retriever = mock_vectorstore.as_retriever.return_value
        mock_embeddings = MagicMock(spec=Embeddings)

        # Mock the retrieved documents
        mock_doc = MagicMock()
        mock_doc.page_content = "Relevant content snippet."
        mock_retriever.get_relevant_documents.return_value = [mock_doc]

        load_path = tmp_path / "faiss_index"
        load_path.mkdir()  # Simulate that the path exists
        # Create dummy files to pass the "any" check
        (load_path / "index.faiss").touch()
        (load_path / "index.pkl").touch()

        # Instantiate and execute
        strategy = RAGRetrievalStrategy(embeddings=mock_embeddings, top_k=3)
        result = strategy.query("What is this about?", load_path)

        # Assertions
        MockFAISS.load_local.assert_called_once_with(
            str(load_path),
            mock_embeddings,
            allow_dangerous_deserialization=True,
        )
        mock_vectorstore.as_retriever.assert_called_once_with(search_kwargs={"k": 3})
        mock_retriever.get_relevant_documents.assert_called_once_with(
            "What is this about?"
        )

        assert "Retrieved Document 1/1" in result
        assert "Relevant content snippet." in result

    @patch("mcp_long_context_reader.strategies.rag_retrieval.FAISS")
    def test_process_and_save_chunks_with_overlap(self, MockFAISS, tmp_path: Path):
        """Tests that process_and_save correctly handles chunk overlap."""
        overlap = 20
        mock_embeddings = MagicMock(spec=Embeddings)
        strategy = RAGRetrievalStrategy(
            embeddings=mock_embeddings, chunk_size=100, chunk_overlap=overlap
        )
        content = "abc" * 200  # Make content long enough to be chunked
        context = LongTextContext(content)
        save_path = tmp_path / "rag_overlap_test"

        # Execute the method
        strategy.process_and_save(context, save_path)

        # Capture the chunks passed to FAISS.from_texts
        MockFAISS.from_texts.assert_called_once()
        _, call_kwargs = MockFAISS.from_texts.call_args
        captured_chunks = call_kwargs["texts"]

        assert len(captured_chunks) > 1
        # The end of the first chunk should match the start of the second chunk
        assert captured_chunks[0][-overlap:] == captured_chunks[1][:overlap]

    @patch("mcp_long_context_reader.strategies.rag_retrieval.FAISS")
    def test_query_returns_message_when_no_docs_found(self, MockFAISS, tmp_path: Path):
        """Tests that a message is returned when the retriever finds no documents."""
        # Setup Mocks
        mock_vectorstore = MockFAISS.load_local.return_value
        mock_retriever = mock_vectorstore.as_retriever.return_value
        mock_embeddings = MagicMock(spec=Embeddings)

        # Mock the retriever to return an empty list
        mock_retriever.get_relevant_documents.return_value = []

        load_path = tmp_path / "faiss_index"
        load_path.mkdir()
        (load_path / "index.faiss").touch()

        # Instantiate and execute
        strategy = RAGRetrievalStrategy(embeddings=mock_embeddings)
        result = strategy.query("What is this about?", load_path)

        assert "No relevant documents found" in result

    def test_process_and_save_handles_empty_document(self, tmp_path: Path):
        """Tests that process_and_save works correctly with an empty document."""
        mock_embeddings = MagicMock(spec=Embeddings)
        strategy = RAGRetrievalStrategy(embeddings=mock_embeddings)
        context = LongTextContext("")
        save_path = tmp_path / "empty_index"

        # We need to mock FAISS for this test
        with patch(
            "mcp_long_context_reader.strategies.rag_retrieval.FAISS"
        ) as MockFAISS:
            strategy.process_and_save(context, save_path)
            # Assert that from_texts was called with a dummy list to create an empty index
            MockFAISS.from_texts.assert_called_once_with([""], mock_embeddings)

    def test_init_raises_error_on_invalid_params(self):
        """Tests that __init__ raises ValueError for invalid chunk sizes."""
        mock_embeddings = MagicMock(spec=Embeddings)
        with pytest.raises(ValueError, match="chunk_size must be at least 50"):
            RAGRetrievalStrategy(embeddings=mock_embeddings, chunk_size=40)

        with pytest.raises(ValueError, match="top_k must be between 1 and 20"):
            RAGRetrievalStrategy(embeddings=mock_embeddings, top_k=0)

        with pytest.raises(ValueError, match="chunk_overlap must be smaller"):
            RAGRetrievalStrategy(
                embeddings=mock_embeddings, chunk_size=100, chunk_overlap=100
            )
