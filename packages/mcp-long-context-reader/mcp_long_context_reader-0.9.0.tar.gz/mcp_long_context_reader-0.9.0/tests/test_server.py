"""
Tests for the MCP Long Context Reader server module.

This acts as an integration test for the server's tool functions,
ensuring that the caching, strategy execution, and security logic
work together correctly.
"""

import os
import sys
import time
import re
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest
from fastmcp import Client
from langchain_core.language_models.chat_models import BaseChatModel
from langchain_core.messages import AIMessage
from langchain_core.outputs import ChatGeneration, ChatResult


def get_text_content(content_obj):
    """Helper function to safely extract text content from MCP response objects."""
    if hasattr(content_obj, "text"):
        return content_obj.text
    elif hasattr(content_obj, "content"):
        return content_obj.content
    else:
        return str(content_obj)


class MockChatModel(BaseChatModel):
    """A test-specific mock LLM that implements the BaseChatModel interface."""

    def __init__(self, **kwargs):
        # Remove extra kwargs that aren't valid BaseChatModel fields
        filtered_kwargs = {
            k: v for k, v in kwargs.items() if k in ["model", "temperature"]
        }
        super().__init__(**filtered_kwargs)
        # Use private attributes to avoid Pydantic field validation
        self._call_count = 0
        self._responses = [
            "This is a mock LLM response.",
            "Updated notes based on the chunk.",
            "Final summary of the document.",
        ]

    def _generate(self, messages, stop=None, run_manager=None, **kwargs):
        """Generate a response for the given messages."""
        self._call_count += 1
        response_idx = (self._call_count - 1) % len(self._responses)
        message = AIMessage(content=self._responses[response_idx])
        generation = ChatGeneration(message=message)
        return ChatResult(generations=[generation])

    def invoke(self, input, config=None, **kwargs):
        """Invoke the model with input and return a message."""
        self._call_count += 1
        response_idx = (self._call_count - 1) % len(self._responses)
        return AIMessage(content=self._responses[response_idx])

    @property
    def _llm_type(self):
        return "mock_chat_model"

    @property
    def call_count(self):
        """Access the call count for tests."""
        return self._call_count


# Global mock setup to ensure consistency across all tests
@pytest.fixture(scope="session", autouse=True)
def setup_global_mocks():
    """Setup global mocks that persist across all test classes."""

    # Create a proper embeddings mock that returns vectors of consistent length
    class MockEmbeddings:
        def embed_documents(self, texts):
            # Return a dummy embedding for each text
            return [[0.1, 0.2, 0.3] for _ in texts]

        def embed_query(self, text):
            return [0.1, 0.2, 0.3]

        def __call__(self, text):
            # Make the object callable for FAISS
            return self.embed_query(text)

    mock_embeddings = MockEmbeddings()

    # Create a more complete FAISS mock that handles save/load operations
    mock_faiss_instance = MagicMock()
    mock_faiss_instance.as_retriever.return_value.get_relevant_documents.return_value = []

    def mock_save_local(path):
        """Mock save_local that creates dummy files to simulate FAISS index."""

        save_path = Path(path)
        save_path.mkdir(parents=True, exist_ok=True)
        # Create dummy FAISS files
        (save_path / "index.faiss").touch()
        (save_path / "index.pkl").touch()

    mock_faiss_instance.save_local = mock_save_local

    mock_faiss = MagicMock()
    mock_faiss.from_texts.return_value = mock_faiss_instance
    mock_faiss.load_local.return_value = mock_faiss_instance

    # Apply global patches
    with (
        patch("langchain_openai.OpenAIEmbeddings", return_value=mock_embeddings),
        patch("langchain_openai.ChatOpenAI", MockChatModel),
        patch("langchain_community.vectorstores.FAISS", mock_faiss),
        patch("langchain_community.embeddings.DashScopeEmbeddings", MagicMock()),
        patch("langchain_community.chat_models.ChatTongyi", MockChatModel),
    ):
        yield


# To test the server, we must set the required environment variables *before*
# the `server` module is imported, because it reads them at startup.
@pytest.fixture
def setup_test_server(tmp_path_factory):
    """
    Sets up a complete, isolated test environment for the server.

    This fixture creates a real temporary directory for the workspace and cache,
    sets the necessary environment variables, and then loads the server module.
    This provides a high-fidelity integration test where the server interacts
    with a real CacheManager and filesystem, while strategies remain mocked.
    """
    # 1. Create real temporary directories
    tmp_path = tmp_path_factory.mktemp("server_tests")
    workspace_dir = tmp_path / "workspace"
    cache_dir = tmp_path / "cache"
    workspace_dir.mkdir()
    cache_dir.mkdir()

    # Create a dummy file for tests to use
    dummy_file = workspace_dir / "doc.txt"
    dummy_file.write_text("This is the content.")

    # 2. Set environment variables to point to our temp dirs
    env = {
        "MCP_WORKSPACE_DIRECTORY": str(workspace_dir),
        "MCP_CACHE_DIRECTORY": str(cache_dir),
        "MCP_API_PROVIDER": "openai",
        "MCP_EMBEDDING_MODEL": "text-embedding-v1",
        "MCP_LLM_MODEL": "gpt-3.5-turbo",
        "OPENAI_API_KEY": "sk-fake-key",
    }

    with patch.dict(os.environ, env, clear=True):
        # 3. Now that the environment is set, import the server
        if "mcp_long_context_reader.server" in sys.modules:
            del sys.modules["mcp_long_context_reader.server"]
        import mcp_long_context_reader.server as server_module

        # Yield the server and the path to the dummy file
        yield server_module, dummy_file


class TestServerInitialization:
    """
    Tests the server's startup logic. It ensures the module handles different
    environment variable configurations correctly upon import.

    Note: These tests do not use the main fixture because they test the import
    process itself under failing conditions.
    """

    def setup_method(self):
        """
        Ensures the server module is re-imported for each test,
        allowing us to test its initialization behavior under
        different environment conditions.
        """
        if "mcp_long_context_reader.server" in sys.modules:
            del sys.modules["mcp_long_context_reader.server"]

    def test_missing_workspace_dir_raises_error(self):
        with patch.dict(os.environ, {}, clear=True):
            with pytest.raises(RuntimeError, match="MCP_WORKSPACE_DIRECTORY"):
                import mcp_long_context_reader.server  # noqa: F401

    def test_missing_embedding_provider_raises_error(self):
        env = {"MCP_WORKSPACE_DIRECTORY": "/tmp", "MCP_CACHE_DIRECTORY": "/tmp/cache"}
        with patch.dict(os.environ, env, clear=True):
            with pytest.raises(RuntimeError, match="MCP_API_PROVIDER"):
                import mcp_long_context_reader.server  # noqa: F401

    def test_missing_api_key_for_openai_raises_error(self):
        env = {
            "MCP_WORKSPACE_DIRECTORY": "/tmp",
            "MCP_CACHE_DIRECTORY": "/tmp/cache",
            "MCP_API_PROVIDER": "openai",
            "MCP_EMBEDDING_MODEL": "text-embedding-v1",
            "MCP_LLM_MODEL": "gpt-3.5-turbo",
        }
        with patch.dict(os.environ, env, clear=True):
            with pytest.raises(RuntimeError, match="OPENAI_API_KEY"):
                import mcp_long_context_reader.server  # noqa: F401


@pytest.mark.asyncio
class TestToolExecution:
    """
    Tests the logic of the MCP tools using a real CacheManager and filesystem,
    with mocked-out strategies.
    """

    async def test_retrieve_with_rag_cache_miss(self, setup_test_server):
        """Tests the full 'cache miss' workflow via the client."""
        server_module, dummy_file_path = setup_test_server

        # --- Act ---
        async with Client(server_module.mcp) as client:
            result_list = await client.call_tool(
                "retrieve_with_rag",
                {"context_path": str(dummy_file_path), "query": "what is love?"},
            )

        # --- Assert ---
        result = get_text_content(result_list[0])
        # The result should contain evidence from the RAG strategy
        assert "Retrieved Document" in result or "No relevant documents found" in result

    async def test_retrieve_with_rag_cache_hit(self, setup_test_server):
        """Tests that a cached result is used on a second identical call."""
        server_module, dummy_file_path = setup_test_server

        def mock_process_creates_file(self, context, save_path):
            """Side effect to simulate file creation by the strategy."""
            save_path.mkdir(parents=True, exist_ok=True)
            (save_path / "index.faiss").touch()

        # Patch the expensive method to track its calls
        with patch(
            "mcp_long_context_reader.strategies.rag_retrieval.RAGRetrievalStrategy.process_and_save",
            side_effect=mock_process_creates_file,
            autospec=True,
        ) as mock_process:
            # --- Act ---
            # First call (cache miss)
            async with Client(server_module.mcp) as client:
                await client.call_tool(
                    "retrieve_with_rag",
                    {"context_path": str(dummy_file_path), "query": "what is love?"},
                )

            # Second call (should be a cache hit)
            async with Client(server_module.mcp) as client:
                await client.call_tool(
                    "retrieve_with_rag",
                    {"context_path": str(dummy_file_path), "query": "what is love?"},
                )

            # --- Assert ---
            # The expensive processing should only have been called once.
            mock_process.assert_called_once()

    async def test_cache_invalidated_by_file_modification(self, setup_test_server):
        """Tests that modifying the source file invalidates the cache."""
        server_module, dummy_file_path = setup_test_server

        def mock_process_creates_file(self, context, save_path):
            """Side effect to simulate file creation by the strategy."""
            save_path.mkdir(parents=True, exist_ok=True)
            (save_path / "index.faiss").touch()

        with patch(
            "mcp_long_context_reader.strategies.rag_retrieval.RAGRetrievalStrategy.process_and_save",
            side_effect=mock_process_creates_file,
            autospec=True,
        ) as mock_process:
            # --- Act ---
            # First call
            async with Client(server_module.mcp) as client:
                await client.call_tool(
                    "retrieve_with_rag",
                    {"context_path": str(dummy_file_path), "query": "any"},
                )

            # Ensure modification time will be different
            time.sleep(0.01)

            # Modify the file
            dummy_file_path.write_text("This is new content.")

            # Second call after modification
            async with Client(server_module.mcp) as client:
                await client.call_tool(
                    "retrieve_with_rag",
                    {"context_path": str(dummy_file_path), "query": "any"},
                )

            # --- Assert ---
            # The expensive processing should have been called twice.
            assert mock_process.call_count == 2

    async def test_path_traversal_attack_is_blocked(self, setup_test_server):
        """Tests that requests to files outside the workspace are rejected."""
        server_module, dummy_file_path = setup_test_server
        workspace_dir = dummy_file_path.parent
        malicious_path = str(workspace_dir / "../../etc/passwd")

        async with Client(server_module.mcp) as client:
            result_list = await client.call_tool(
                "retrieve_with_rag",
                {"context_path": malicious_path, "query": "give me secrets"},
            )

        result_text = get_text_content(result_list[0])
        assert "is outside the allowed workspace" in result_text

    async def test_search_with_regex_succeeds(self, setup_test_server):
        """Tests that the search_with_regex tool can be called successfully."""
        server_module, dummy_file_path = setup_test_server

        async with Client(server_module.mcp) as client:
            result_list = await client.call_tool(
                "search_with_regex",
                {"context_path": str(dummy_file_path), "regex_pattern": "content"},
            )

        result = get_text_content(result_list[0])
        # Should either find the regex pattern or return no matches
        assert "content" in result and "No matches found" not in result

    async def test_search_with_regex_case_sensitivity(self, setup_test_server):
        """Tests that the case_sensitive flag works via the MCP tool."""
        server_module, dummy_file_path = setup_test_server
        # Overwrite file with case-specific content
        dummy_file_path.write_text("Hello hello")

        # 1. Test case-insensitive search
        async with Client(server_module.mcp) as client:
            result_list_insensitive = await client.call_tool(
                "search_with_regex",
                {
                    "context_path": str(dummy_file_path),
                    "regex_pattern": "hello",
                    "case_sensitive": False,
                },
            )
        result_insensitive = get_text_content(result_list_insensitive[0])
        matches_insensitive = re.findall(r"--- Result \d+/\d+ ---", result_insensitive)
        assert len(matches_insensitive) == 2

        # 2. Test case-sensitive search (the default)
        async with Client(server_module.mcp) as client:
            result_list_sensitive = await client.call_tool(
                "search_with_regex",
                {
                    "context_path": str(dummy_file_path),
                    "regex_pattern": "hello",
                    "case_sensitive": True,
                },
            )
        result_sensitive = get_text_content(result_list_sensitive[0])
        matches_sensitive = re.findall(r"--- Result \d+/\d+ ---", result_sensitive)
        assert len(matches_sensitive) == 1

    async def test_summarize_with_map_reduce_succeeds(self, setup_test_server):
        """Tests that a tool requiring an LLM can be called successfully."""
        server_module, dummy_file_path = setup_test_server

        async with Client(server_module.mcp) as client:
            result_list = await client.call_tool(
                "summarize_with_map_reduce",
                {"context_path": str(dummy_file_path), "question": "summarize"},
            )

        result = get_text_content(result_list[0])
        # Should contain a summary response from the mock LLM
        # The mock LLM returns different responses based on call count
        mock_responses = [
            "This is a mock LLM response.",
            "Updated notes based on the chunk.",
            "Final summary of the document.",
        ]
        assert any(response in result for response in mock_responses)
        # The result should not be an error message
        assert not result.startswith("Error:")

    async def test_strategy_initialization_failure_returns_error(
        self, setup_test_server
    ):
        """
        Tests that if a strategy fails to initialize, the server returns a
        graceful error message instead of crashing.
        """
        server_module, dummy_file_path = setup_test_server

        # Patch the RAG strategy's __init__ to simulate a failure.
        with patch(
            "mcp_long_context_reader.strategies.rag_retrieval.RAGRetrievalStrategy.__init__",
            side_effect=ValueError("Simulated init error"),
        ):
            async with Client(server_module.mcp) as client:
                result_list = await client.call_tool(
                    "retrieve_with_rag",
                    {
                        "context_path": str(dummy_file_path),
                        "query": "any query",
                    },
                )

        assert "Error initializing strategy:" in get_text_content(result_list[0])
        assert "Simulated init error" in get_text_content(result_list[0])

    async def test_summarize_with_sequential_notes_succeeds(self, setup_test_server):
        """Tests that the sequential notes strategy works with real LLM."""
        server_module, dummy_file_path = setup_test_server

        async with Client(server_module.mcp) as client:
            result_list = await client.call_tool(
                "summarize_with_sequential_notes",
                {
                    "context_path": str(dummy_file_path),
                    "question": "What is this about?",
                },
            )

        result = get_text_content(result_list[0])
        # Should contain notes from our mock LLM
        assert len(result) > 0
        assert not result.startswith("Error:")

    async def test_llm_strategies_receive_llm_instance(self, setup_test_server):
        """Tests that LLM-dependent strategies are properly initialized with LLM instances."""
        server_module, dummy_file_path = setup_test_server

        # Test both LLM-dependent strategies
        strategies_to_test = [
            ("summarize_with_sequential_notes", {"question": "test"}),
            ("summarize_with_map_reduce", {"question": "test"}),
        ]

        for tool_name, params in strategies_to_test:
            params["context_path"] = str(dummy_file_path)
            async with Client(server_module.mcp) as client:
                result_list = await client.call_tool(tool_name, params)

            result = get_text_content(result_list[0])
            # If LLM instance wasn't passed, we'd get a KeyError about missing 'llm'
            assert "KeyError" not in result
            assert "An 'llm' instance must be provided" not in result

    async def test_glance_succeeds(self, setup_test_server):
        """Tests that the glance tool can be called successfully."""
        server_module, dummy_file_path = setup_test_server
        dummy_file_path.write_text("Line 1\nLine 2")  # 13 characters

        async with Client(server_module.mcp) as client:
            result_list = await client.call_tool(
                "glance",
                {"context_path": str(dummy_file_path)},
            )

        result = get_text_content(result_list[0])
        assert "Showing the first 13 characters" in result
        assert "of 2 total lines" in result
        assert "Line 1\nLine 2" in result

    async def test_glance_file_not_found(self, setup_test_server):
        """Tests that glance returns an error for a non-existent file."""
        server_module, dummy_file_path = setup_test_server
        non_existent_path = dummy_file_path.parent / "no_such_file.txt"

        async with Client(server_module.mcp) as client:
            result_list = await client.call_tool(
                "glance",
                {"context_path": str(non_existent_path)},
            )

        result = get_text_content(result_list[0])
        assert "Error: File not found" in result

    async def test_glance_long_file_is_truncated(self, setup_test_server):
        """Tests that glance correctly truncates very long files."""
        server_module, dummy_file_path = setup_test_server
        # Get the char_limit directly from the running server instance
        # to avoid hardcoding and make the test more robust.
        char_limit = server_module.inspector.char_limit
        long_content = "A" * (char_limit + 1000)
        dummy_file_path.write_text(long_content)

        async with Client(server_module.mcp) as client:
            result_list = await client.call_tool(
                "glance",
                {"context_path": str(dummy_file_path)},
            )

        result = get_text_content(result_list[0])

        # Check header for correct truncation count
        assert f"Showing the first {char_limit} characters" in result
        assert "of 1 total lines" in result

        # Check that the snippet is exactly the truncated content
        snippet = result.split("---\n", 1)[1]
        assert len(snippet) == char_limit
        assert snippet == "A" * char_limit

    async def test_glance_with_context_text(self, setup_test_server):
        """Tests that glance supports context_text input, and deletes temporary files immediately."""
        server_module, dummy_file_path = setup_test_server
        test_text = "Line 1\nLine 2"
        async with Client(server_module.mcp) as client:
            result_list = await client.call_tool(
                "glance",
                {"context_text": test_text},
            )
        result = get_text_content(result_list[0])
        assert "Showing the first 13 characters" in result
        assert "of 2 total lines" in result
        assert "Line 1\nLine 2" in result
        # Check that there are no leftover tmp_str_ files in the cache directory
        cache_dir = server_module.CACHE_DIR
        assert not any(f.name.startswith("tmp_str_") for f in cache_dir.iterdir()), (
            "Temporary files not deleted"
        )

    async def test_search_with_regex_with_context_text(self, setup_test_server):
        """Tests that search_with_regex supports context_text input."""
        server_module, _ = setup_test_server
        test_text = "This is the content."
        async with Client(server_module.mcp) as client:
            result_list = await client.call_tool(
                "search_with_regex",
                {"context_text": test_text, "regex_pattern": "content"},
            )
        result = get_text_content(result_list[0])
        assert "content" in result and "No matches found" not in result
        cache_dir = server_module.CACHE_DIR
        assert not any(f.name.startswith("tmp_str_") for f in cache_dir.iterdir()), (
            "Temporary files not deleted"
        )

    async def test_retrieve_with_rag_with_context_text(self, setup_test_server):
        """Tests that retrieve_with_rag supports context_text input."""
        server_module, _ = setup_test_server
        test_text = "This is the content."
        async with Client(server_module.mcp) as client:
            result_list = await client.call_tool(
                "retrieve_with_rag",
                {"context_text": test_text, "query": "content"},
            )
        result = get_text_content(result_list[0])
        assert "Retrieved Document" in result or "No relevant documents found" in result
        cache_dir = server_module.CACHE_DIR
        assert not any(f.name.startswith("tmp_str_") for f in cache_dir.iterdir()), (
            "Temporary files not deleted"
        )

    async def test_summarize_with_map_reduce_with_context_text(self, setup_test_server):
        """Tests that summarize_with_map_reduce supports context_text input."""
        server_module, _ = setup_test_server
        test_text = "This is the content."
        async with Client(server_module.mcp) as client:
            result_list = await client.call_tool(
                "summarize_with_map_reduce",
                {"context_text": test_text, "question": "summarize"},
            )
        result = get_text_content(result_list[0])
        mock_responses = [
            "This is a mock LLM response.",
            "Updated notes based on the chunk.",
            "Final summary of the document.",
        ]
        assert any(response in result for response in mock_responses)
        assert not result.startswith("Error:")
        cache_dir = server_module.CACHE_DIR
        assert not any(f.name.startswith("tmp_str_") for f in cache_dir.iterdir()), (
            "Temporary files not deleted"
        )

    async def test_summarize_with_sequential_notes_with_context_text(
        self, setup_test_server
    ):
        """Tests that summarize_with_sequential_notes supports context_text input."""
        server_module, _ = setup_test_server
        test_text = "This is the content."
        async with Client(server_module.mcp) as client:
            result_list = await client.call_tool(
                "summarize_with_sequential_notes",
                {"context_text": test_text, "question": "What is this about?"},
            )
        result = get_text_content(result_list[0])
        assert len(result) > 0
        assert not result.startswith("Error:")
        cache_dir = server_module.CACHE_DIR
        assert not any(f.name.startswith("tmp_str_") for f in cache_dir.iterdir()), (
            "Temporary files not deleted"
        )


class TestServerInitializationWithDashScope:
    """
    Tests the server's startup logic specifically for the DashScope provider.
    """

    def setup_method(self):
        if "mcp_long_context_reader.server" in sys.modules:
            del sys.modules["mcp_long_context_reader.server"]

    def test_dashscope_initialization_succeeds(self):
        """
        Tests that the server initializes correctly with the dashscope provider
        if the required API key is present.
        """
        env = {
            "MCP_WORKSPACE_DIRECTORY": "/tmp",
            "MCP_CACHE_DIRECTORY": "/tmp/cache",
            "MCP_API_PROVIDER": "dashscope",
            "MCP_EMBEDDING_MODEL": "text-embedding-v1",
            "MCP_LLM_MODEL": "qwen-max",
            "DASHSCOPE_API_KEY": "fake_key_for_dashscope",
        }
        with (
            patch.dict(os.environ, env, clear=True),
            patch("langchain_community.embeddings.DashScopeEmbeddings", MagicMock()),
            patch("langchain_community.chat_models.ChatTongyi", MockChatModel),
        ):
            try:
                import mcp_long_context_reader.server  # noqa: F401
            except RuntimeError as e:
                pytest.fail(f"Server failed to initialize with DashScope: {e}")

    def test_dashscope_initialization_fails_without_key(self):
        """
        Tests that server initialization fails if dashscope is the provider
        but the API key is missing.
        """
        env = {
            "MCP_WORKSPACE_DIRECTORY": "/tmp",
            "MCP_CACHE_DIRECTORY": "/tmp/cache",
            "MCP_API_PROVIDER": "dashscope",
            "MCP_EMBEDDING_MODEL": "text-embedding-v1",
            "MCP_LLM_MODEL": "qwen-max",
        }
        with patch.dict(os.environ, env, clear=True):
            with pytest.raises(RuntimeError, match="DASHSCOPE_API_KEY"):
                import mcp_long_context_reader.server  # noqa: F401
