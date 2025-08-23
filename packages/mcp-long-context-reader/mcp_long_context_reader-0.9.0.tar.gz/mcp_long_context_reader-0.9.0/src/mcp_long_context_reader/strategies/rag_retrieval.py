from pathlib import Path
from typing import List

from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import FAISS
from langchain_core.embeddings import Embeddings

from mcp_long_context_reader.context import LongTextContext
from mcp_long_context_reader.strategies.base import SearchStrategy


class RAGRetrievalStrategy(SearchStrategy):
    """A search strategy that uses a RAG pipeline to find relevant chunks."""

    def __init__(self, embeddings: Embeddings, **strategy_params):
        super().__init__(**strategy_params)
        self.embeddings = embeddings
        self.chunk_size = self.params.get("chunk_size", 1000)
        self.chunk_overlap = self.params.get("chunk_overlap", 200)
        self.top_k = self.params.get("top_k", 4)

        if self.chunk_size < 50:
            raise ValueError("chunk_size must be at least 50.")
        if not 1 <= self.top_k <= 20:
            raise ValueError("top_k must be between 1 and 20.")
        if self.chunk_overlap >= self.chunk_size:
            raise ValueError("chunk_overlap must be smaller than chunk_size.")

    def process_and_save(self, context: LongTextContext, save_path: Path):
        """
        Splits context, creates a FAISS vector store, and saves it locally.
        """
        text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=self.chunk_size,
            chunk_overlap=self.chunk_overlap,
            length_function=len,
        )
        chunks = text_splitter.split_text(context.content)

        if not chunks:
            # Create a dummy empty index if there's no content
            dummy_index = FAISS.from_texts([""], self.embeddings)
            dummy_index.save_local(str(save_path))
            return

        vectorstore = FAISS.from_texts(texts=chunks, embedding=self.embeddings)
        vectorstore.save_local(str(save_path))

    def query(self, query: str, load_path: Path) -> str:
        """
        Loads a local FAISS index and retrieves relevant documents.
        """
        if not load_path.exists() or not any(load_path.iterdir()):
            return "Error: Cached RAG index not found or is empty."

        try:
            vectorstore = FAISS.load_local(
                str(load_path), self.embeddings, allow_dangerous_deserialization=True
            )
        except Exception as e:
            return f"Error loading RAG index: {e}"

        retriever = vectorstore.as_retriever(search_kwargs={"k": self.top_k})
        docs = retriever.get_relevant_documents(query)

        if not docs:
            return "No relevant documents found for the query."

        results: List[str] = []
        for i, doc in enumerate(docs):
            results.append(
                f"--- Retrieved Document {i + 1}/{len(docs)} ---\n{doc.page_content}"
            )

        return "\n\n".join(results)
