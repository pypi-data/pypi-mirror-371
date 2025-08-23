import datetime
import os
from pathlib import Path
from typing import Optional

from fastmcp import FastMCP
from langchain_core.embeddings import Embeddings
from langchain_core.language_models.chat_models import BaseChatModel

from mcp_long_context_reader.cache_manager import CacheManager
from mcp_long_context_reader.context import LongTextContext
from mcp_long_context_reader.inspector import FileInspector
from mcp_long_context_reader.strategies import (
    MapReduceSummaryStrategy,
    RAGRetrievalStrategy,
    RegexSearchStrategy,
    SequentialNotesStrategy,
)

# --- Configuration from Environment Variables ---
# Required
try:
    WORKSPACE_DIR = Path(os.environ["MCP_WORKSPACE_DIRECTORY"]).resolve()
    CACHE_DIR = Path(os.environ["MCP_CACHE_DIRECTORY"]).resolve()
    API_PROVIDER = os.environ["MCP_API_PROVIDER"].lower()
    EMBEDDING_MODEL = os.environ["MCP_EMBEDDING_MODEL"]
    LLM_MODEL = os.environ["MCP_LLM_MODEL"]
except KeyError as e:
    raise RuntimeError(f"Critical environment variable {e} is not set.")

# Optional
OPENAI_API_BASE_URL = os.environ.get("OPENAI_API_BASE_URL", None)

# --- Global Instances ---
mcp = FastMCP(
    "Long Context Reader",
)
inspector = FileInspector(char_limit=5000)
cache_manager = CacheManager(
    cache_dir=CACHE_DIR, manifest_path=CACHE_DIR / "manifest.json"
)
STRATEGY_MAP = {
    "RegexSearch": RegexSearchStrategy,
    "RAGRetrieval": RAGRetrievalStrategy,
    "SequentialNotes": SequentialNotesStrategy,
    "MapReduceSummary": MapReduceSummaryStrategy,
}


def _create_global_embeddings() -> Embeddings:
    """Creates a global embedding model instance based on environment variables."""
    if API_PROVIDER == "openai":
        from langchain_openai import OpenAIEmbeddings

        if os.environ.get("OPENAI_API_KEY") is None:
            raise RuntimeError("OPENAI_API_KEY must be set for OpenAI provider.")
        # return OpenAIEmbeddings(model=EMBEDDING_MODEL)
        if OPENAI_API_BASE_URL:
            return OpenAIEmbeddings(model=EMBEDDING_MODEL, base_url=OPENAI_API_BASE_URL)
        else:
            return OpenAIEmbeddings(model=EMBEDDING_MODEL)
    elif API_PROVIDER == "dashscope":
        from langchain_community.embeddings import DashScopeEmbeddings

        if os.environ.get("DASHSCOPE_API_KEY") is None:
            raise RuntimeError("DASHSCOPE_API_KEY must be set for DashScope provider.")
        return DashScopeEmbeddings(model=EMBEDDING_MODEL)
    else:
        raise ValueError(f"Unknown embedding provider: {API_PROVIDER}")


def _create_global_llm() -> BaseChatModel:
    """Creates a global LLM instance based on environment variables."""
    if API_PROVIDER == "openai":
        from langchain_openai import ChatOpenAI

        if os.environ.get("OPENAI_API_KEY") is None:
            raise RuntimeError("OPENAI_API_KEY must be set for OpenAI provider.")
        # return ChatOpenAI(model=LLM_MODEL, temperature=0)
        if OPENAI_API_BASE_URL:
            return ChatOpenAI(
                model=LLM_MODEL, temperature=0, base_url=OPENAI_API_BASE_URL
            )
        else:
            return ChatOpenAI(model=LLM_MODEL, temperature=0)
    elif API_PROVIDER == "dashscope":
        from langchain_community.chat_models import ChatTongyi
        from pydantic import SecretStr

        if os.environ.get("DASHSCOPE_API_KEY") is None:
            raise RuntimeError("DASHSCOPE_API_KEY must be set for DashScope provider.")
        return ChatTongyi(
            model=LLM_MODEL, api_key=SecretStr(os.environ["DASHSCOPE_API_KEY"])
        )
    else:
        raise ValueError(f"Unknown provider for LLM: {API_PROVIDER}")


try:
    GLOBAL_EMBEDDINGS = _create_global_embeddings()
    GLOBAL_LLM = _create_global_llm()
except (ImportError, RuntimeError, ValueError) as e:
    raise RuntimeError(f"Failed to initialize models: {e}") from e


# --- Internal Helper Function ---
def _execute_strategy(
    context_path_str: Optional[str] = None,
    context_text: Optional[str] = None,
    query: Optional[str] = None,
    strategy_name: Optional[str] = None,
    strategy_params: Optional[dict] = None,
    query_params: Optional[dict] = None,
) -> str:
    """A centralized function to handle the cache and execution logic."""

    if context_path_str is None and context_text is None:
        return "Error: Exactly one of context_path or context_text must be provided."
    if context_path_str is not None and context_text is not None:
        return "Error: Exactly one of context_path or context_text must be provided. Do NOT provide both."
    if query is None or query == "":
        return "Error: query must be provided."
    if strategy_name is None or strategy_name not in STRATEGY_MAP:
        return f"Error: Invalid strategy name: {strategy_name}"
    if strategy_params is None:
        strategy_params = {}
    if query_params is None:
        query_params = {}

    tmp_file_path = None
    try:
        if context_text is not None:
            # TODO: Put this creating temp file logic into cache manager
            # 1. Write to temporary file
            text_hash = datetime.datetime.now().strftime("%Y%m%d%H%M%S%f")
            tmp_file_path = CACHE_DIR / f"tmp_str_{text_hash}.txt"
            tmp_file_path.write_text(context_text, encoding="utf-8")
            context_path = tmp_file_path.resolve()
        else:
            if context_path_str is None:
                raise ValueError("context_path is None")
            context_path = Path(context_path_str).resolve()

        # 2. Security Check
        if (
            not str(context_path).startswith(str(WORKSPACE_DIR))
            and tmp_file_path is None
        ):
            return f"Error: Path '{context_path}' is outside the allowed workspace."
        if not context_path.exists():
            return f"Error: File not found at '{context_path}'."

        # 3. Generate Cache Key
        try:
            key = cache_manager.generate_key(
                context_path, strategy_name, strategy_params
            )
        except FileNotFoundError:
            return f"Error: File disappeared after check: '{context_path}'."

        # 4. Check Cache & Execute
        strategy_class = STRATEGY_MAP[strategy_name]
        try:
            if strategy_name == "RAGRetrieval":
                strategy = strategy_class(
                    embeddings=GLOBAL_EMBEDDINGS, **strategy_params
                )
            elif strategy_name in ["SequentialNotes", "MapReduceSummary"]:
                strategy = strategy_class(llm=GLOBAL_LLM, **strategy_params)
            else:
                strategy = strategy_class(**strategy_params)
        except (ValueError, KeyError) as e:
            return f"Error initializing strategy: {e}"

        cached_path = cache_manager.get(key)
        if cached_path:  # Cache Hit
            result = strategy.query(query, load_path=cached_path, **query_params)
        else:  # Cache Miss
            context = LongTextContext.from_file(context_path)
            new_cache_path = cache_manager.put(key)
            strategy.process_and_save(context, save_path=new_cache_path)
            result = strategy.query(query, load_path=new_cache_path, **query_params)
        return result

    finally:
        # Delete temporary file after use
        if tmp_file_path is not None and tmp_file_path.exists():
            tmp_file_path.unlink()


# --- MCP Tool Definitions ---
@mcp.tool
def glance(
    context_path: Optional[str] = None, context_text: Optional[str] = None
) -> str:
    """
    Provides a quick look at the beginning of a file or a string, showing the first few thousands
    characters and total line count.
    Exactly one of context_path or context_text must be provided. Do NOT provide both.

    Args:
        context_path (str): The path to the file to glance at.
        context_text (str): The text content to glance at.

    Returns:
        A string containing a snippet of the file/text and metadata.
    """
    if context_path is not None and context_text is not None:
        return "Error: Exactly one of context_path or context_text must be provided. Do NOT provide both."
    if context_path is None and context_text is None:
        return "Error: Exactly one of context_path or context_text must be provided."

    if context_path is None and context_text is not None:
        # Write to temporary file, reuse inspector.glance
        text_hash = datetime.datetime.now().strftime("%Y%m%d%H%M%S%f")
        tmp_file_path = CACHE_DIR / f"tmp_str_{text_hash}.txt"
        tmp_file_path.write_text(context_text, encoding="utf-8")
        try:
            result = inspector.glance(tmp_file_path)
        finally:
            if tmp_file_path.exists():
                try:
                    tmp_file_path.unlink()
                except Exception:
                    pass
        return result
    else:
        # 1. Security Check
        try:
            if context_path is None:
                raise ValueError("context_path is None")
            resolved_path = Path(context_path).resolve()
        except Exception as e:
            return f"Error resolving path '{context_path}': {e}"
        if not str(resolved_path).startswith(str(WORKSPACE_DIR)):
            return f"Error: Path '{resolved_path}' is outside the allowed workspace."
        if not resolved_path.exists():
            return f"Error: File not found at '{resolved_path}'."

        # 2. Execute
        return inspector.glance(resolved_path)


@mcp.tool
def search_with_regex(
    context_path: Optional[str] = None,
    context_text: Optional[str] = None,
    regex_pattern: Optional[str] = None,
    case_sensitive: bool = True,
) -> str:
    r"""
    Searches a document for a regex pattern and returns matching snippets.
    Exactly one of context_path or context_text must be provided. Do NOT provide both.

    Args:
        context_path (str, optional): The path to the context file.
        context_text (str, optional): The text content to search.
        regex_pattern (str, optional): The regex pattern to search for.
        case_sensitive (bool, default=True): Whether to match case-sensitively.

    Returns:
        str: A string containing the matching snippets.
    """
    if regex_pattern is None or regex_pattern == "":
        return "Error: regex_pattern must be provided."

    params = {"context_window": 200, "max_matches": 20, "max_match_display_len": 200}
    query_params = {"case_sensitive": case_sensitive}
    return _execute_strategy(
        context_path_str=context_path,
        context_text=context_text,
        query=regex_pattern,
        strategy_name="RegexSearch",
        strategy_params=params,
        query_params=query_params,
    )


@mcp.tool
def retrieve_with_rag(
    context_path: Optional[str] = None,
    context_text: Optional[str] = None,
    query: Optional[str] = None,
) -> str:
    """
    Retrieves relevant passages from a document or string based on a query using RAG.
    Exactly one of context_path or context_text must be provided. Do NOT provide both.

    Args:
        context_path (str): The path to the context file.
        context_text (str): The text content to search.
        query (str): The query to search for.

    Returns:
        str: A string containing the relevant passages.
    """
    params = {"chunk_size": 512, "chunk_overlap": 100, "top_k": 5}
    return _execute_strategy(
        context_path_str=context_path,
        context_text=context_text,
        query=query,
        strategy_name="RAGRetrieval",
        strategy_params=params,
        query_params=None,
    )


@mcp.tool
def summarize_with_map_reduce(
    context_path: Optional[str] = None,
    context_text: Optional[str] = None,
    question: Optional[str] = None,
) -> str:
    """
    Summarizes a document or string using a map-reduce approach.
    Exactly one of context_path or context_text must be provided. Do NOT provide both.
    Note: This operation is resource-intensive and can be time-consuming.

    Args:
        context_path (str): The path to the context file.
        context_text (str): The text content to summarize.
        question (str): The question for each chunk to answer.

    Returns:
        str: A string containing the overall summary.
    """
    params = {
        "chunk_size": 10000,
        "chunk_overlap": 1000,
        "query_timeout": 180,
        "max_concurrency": 16,
    }
    return _execute_strategy(
        context_path_str=context_path,
        context_text=context_text,
        query=question,
        strategy_name="MapReduceSummary",
        strategy_params=params,
        query_params=None,
    )


@mcp.tool
def summarize_with_sequential_notes(
    context_path: Optional[str] = None,
    context_text: Optional[str] = None,
    question: Optional[str] = None,
) -> str:
    """
    Reads a document or string sequentially to synthesize query-aware notes.
    Exactly one of context_path or context_text must be provided. Do NOT provide both.
    Note: This operation is resource-intensive and can be time-consuming.

    Args:
        context_path (str): The path to the context file.
        context_text (str): The text content to synthesize notes from.
        question (str): The goal of the note-taking.

    Returns:
        str: A string containing the synthesized notes, focusing on the question.
    """
    params = {"chunk_size": 10000, "chunk_overlap": 1000, "chunk_timeout": 60}
    return _execute_strategy(
        context_path_str=context_path,
        context_text=context_text,
        query=question,
        strategy_name="SequentialNotes",
        strategy_params=params,
        query_params=None,
    )


def main():
    """
    Main function to run the server.
    """
    mcp.run()


if __name__ == "__main__":
    # Directly run the server. Transport is stdio.
    # When running with fastmcp instead of python, this is ignored.
    main()
