import pickle
from pathlib import Path

from langchain.prompts import PromptTemplate
from langchain.text_splitter import RecursiveCharacterTextSplitter

from mcp_long_context_reader.context import LongTextContext
from mcp_long_context_reader.strategies.base import SearchStrategy
from mcp_long_context_reader.utils import timeout, TimeoutError

NOTE_TAKING_PROMPT = PromptTemplate.from_template(
    """Your primary mission is to answer the "Original Question" using the provided document. You will read the document in chunks and progressively build a "Reading Note".

**Your Task:**
Read the "New Chunk of Document" and critically REVISE the "Existing Reading Note". Your goal is to create a new, updated note that is a focused collection of key facts and information *essential* for answering the question.

**Key Instructions:**
1.  **Relevance is paramount:** Only include information that directly or potentially helps answer the "Original Question". Discard any irrelevant details if they don't contribute to the final answer.
2.  **Actively Refine, Don't Just Append:** Do not simply add new information to the end of the old note. Instead, integrate the new findings. This means you might need to:
    - **Merge:** Combine new details with existing points to make them more complete.
    - **Refine:** Replace general statements with more specific information from the new chunk.
    - **Delete:** Remove any information from the existing note that you now realize is irrelevant or less important.
3.  **No-Change Option:** If the "New Chunk of Document" contains no relevant information for answering the question, it is totally okay to output the "Existing Reading Note" again, completely unmodified.
4.  **Be Concise:** Keep the note as short and dense as possible. It is a working document, not a comprehensive summary of everything.
5. **Don't Rush for a Conclusion:** It is crucial to process all chunks before making a final conclusion.
6.  **Output Format:** Your output must ONLY be the full text of the newly revised "Updated Reading Note". Do not include any other text, greetings, or explanations.

---

**Progress:** {chunk_idx} out of {total_chunks}

**Original Question:**
{question}

**Existing Reading Note:**
{note}

**New Chunk of Document:**
{chunk}

---

**Updated Reading Note:**
"""
)

# FINAL_ANSWER_PROMPT = PromptTemplate.from_template(
#     """
# You have finished reading the document by reviewing it chunk by chunk and taking notes.
# Now, using only your notes, answer the user's original question.

# The user's question was: "{query}"

# Your complete notes are:
# ---
# {notes}
# ---

# Your final answer:
# """
# )


class SequentialNotesStrategy(SearchStrategy):
    """
    A strategy that uses an LLM to iteratively read chunks of a document
    and take query-aware notes.
    """

    def __init__(self, **strategy_params):
        super().__init__(**strategy_params)
        self.chunk_size = self.params.get("chunk_size", 4000)
        self.chunk_overlap = self.params.get("chunk_overlap", 200)
        self.chunk_timeout = self.params.get(
            "chunk_timeout", 60
        )  # Default 60 seconds per chunk

        if self.chunk_size < 200:
            raise ValueError("chunk_size must be at least 200.")
        if self.chunk_overlap >= self.chunk_size:
            raise ValueError("chunk_overlap must be smaller than chunk_size.")
        if self.chunk_timeout <= 0:
            raise ValueError("chunk_timeout must be positive.")

        try:
            self.llm = self.params["llm"]
        except KeyError:
            raise KeyError(
                "An 'llm' instance must be provided for SequentialNotesStrategy."
            )

    def _process_single_chunk(
        self, query: str, note: str, chunk: str, chunk_idx: int, total_chunks: int
    ) -> str:
        """
        Process a single chunk and update the note.

        Args:
            query: The original question
            note: The existing reading note
            chunk: The current chunk to process
            chunk_idx: Current chunk index
            total_chunks: Total number of chunks

        Returns:
            Updated note string
        """
        prompt = NOTE_TAKING_PROMPT.format(
            question=query,
            note=note,
            chunk=chunk,
            chunk_idx=chunk_idx,
            total_chunks=total_chunks,
        )
        # This is a bit ugly, but LangChain's .invoke returns a message object
        # and we just need the content string.
        response = self.llm.invoke(prompt)
        return response.content if hasattr(response, "content") else str(response)

    def process_and_save(self, context: LongTextContext, save_path: Path):
        """
        Splits the context into chunks and saves the list of chunks to a file.
        """
        text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=self.chunk_size,
            chunk_overlap=self.chunk_overlap,
        )
        chunks = text_splitter.split_text(context.content)

        with open(save_path, "wb") as f:
            pickle.dump(chunks, f)

    def query(self, query: str, load_path: Path) -> str:
        """
        Loads chunks, iteratively takes notes, and returns the final notes.
        """
        if not load_path.exists():
            return "Error: Cached chunks not found."

        with open(load_path, "rb") as f:
            chunks = pickle.load(f)

        if not chunks:
            return "The document is empty."

        note = "[No notes yet]"
        total_chunks = len(chunks)

        for i, chunk in enumerate(chunks):

            @timeout(self.chunk_timeout)
            def _process_chunk_decorated():
                return self._process_single_chunk(
                    query=query,
                    note=note,
                    chunk=chunk,
                    chunk_idx=i,
                    total_chunks=total_chunks,
                )

            try:
                note = _process_chunk_decorated()
            except TimeoutError as e:
                return (
                    f"Sequential notes processing timed out: {str(e)}. "
                    f"Processed {i} out of {total_chunks} chunks.\n\n"
                    f"Note at timeout:\n\n{note}"
                )
            except Exception:
                # Chunk processing failed, skip current chunk.
                continue

        # Per our design, we return the final notes, not a generated answer.
        return note
