import pickle
from pathlib import Path

from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_core.documents import Document
from langchain_core.prompts import PromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain.chains.combine_documents import create_stuff_documents_chain

from mcp_long_context_reader.context import LongTextContext
from mcp_long_context_reader.strategies.base import SearchStrategy
from mcp_long_context_reader.utils import timeout, TimeoutError


MAP_PROMPT_TEMPLATE = """---------- Instruction ----------
Your task is to answer the given "Question" based *solely* on the provided "Text Context".

**Crucial Rules for Answering:**
1.  **Strictly Confine to Text Context:** Your answer MUST be derived exclusively from the "Text Context". Do NOT use any external knowledge, prior information, or make assumptions beyond what is explicitly stated in the text.
2.  **Cite Evidence If Possible:** When the text context provides direct support for your answer, try to include a brief, relevant quote from the "Text Context" to support your statement. For example: "The text states, '...relevant quote...'. Therefore, [your answer]." If direct quoting is too verbose for the specific answer part, ensure your statement is a direct paraphrase of information present.
3.  **Handle Missing or Partial Information Accurately:**
    -   **Full Answer Possible:** If the "Text Context" contains all necessary information to fully answer the "Question", provide a comprehensive answer with citations/references to the text.
    -   **Partial Answer Possible:** If the "Text Context" allows you to answer *part* of the "Question" but not all of it, provide the partial answer clearly stating what can be answered from the text and what information is missing. For example: "Based on the provided text: [answer to part of the question with citation]. However, the text does not provide information regarding [specific part of the question that is unanswered]."
    -   **Information Not Found:** If the "Text Context" does not contain any relevant information to answer the "Question", you MUST respond with: "The provided part of the text does not contain any information to answer the question." Do not attempt to guess or infer.
4.  **Be Direct and Concise:** Answer the question directly. Avoid unnecessary elaboration or conversational fillers not directly supported by the text.

**Input Format (You will receive):**
1.  Text Context: The content of a specific document chunk.
2.  Question: The question to answer based *only* on the "Text Context".

**Your Response:**
Provide your answer directly based on the rules above.
---------- Input ----------
{text}
---------- Question ----------
{question}
"""
MAP_PROMPT = PromptTemplate.from_template(MAP_PROMPT_TEMPLATE)


REDUCE_PROMPT_TEMPLATE = """---------- Instruction ----------
Your task is to synthesize a final answer to the "Question" based on the provided "Summaries". The "Summaries" are answers generated from different parts of a long document, where each summary is a potential answer to the question based on a chunk of the document.

**Crucial Rules for Synthesizing:**
1.  **Synthesize, Don't Just List:** Combine the information from the "Summaries" into a coherent and unified final answer. Do not simply list the individual summaries. Identify recurring themes, pieces of evidence, and consolidate them.
2.  **Base on Provided Summaries:** Your final answer must be based *only* on the information present in the "Summaries". Do not add external knowledge or make assumptions.
3.  **Handle Contradictions or Missing Info:**
    - If some summaries provide an answer and others say the information is missing, prioritize the ones with information, assuming they come from relevant parts of the document.
    - If summaries are contradictory, point out the contradiction in your final answer.
    - If ALL summaries indicate that the information is not found, your final answer must be: "The document does not contain information to answer the question."
4.  **Be Comprehensive and Direct:** Ensure the final answer directly addresses the "Question" as completely as possible based on the given summaries.

**Input Format (You will receive):**
1.  Summaries: A collection of partial answers or notes from different document chunks.
2.  Question: The original question you need to answer.

**Your Response:**
Provide a single, synthesized, and well-formulated final answer.
---------- Input ----------
{context}
---------- Question ----------
{question}
"""
REDUCE_PROMPT = PromptTemplate.from_template(REDUCE_PROMPT_TEMPLATE)


class MapReduceSummaryStrategy(SearchStrategy):
    """
    A strategy that uses a Map-Reduce approach to summarize the document.
    """

    def __init__(self, **strategy_params):
        super().__init__(**strategy_params)
        self.chunk_size = self.params.get("chunk_size", 8000)
        self.chunk_overlap = self.params.get("chunk_overlap", 400)
        self.query_timeout = self.params.get(
            "query_timeout", 180
        )  # 3-minute timeout for the whole query
        self.max_concurrency = self.params.get("max_concurrency", 16)

        if self.chunk_size < 500:
            raise ValueError("chunk_size must be at least 500.")
        if self.chunk_overlap >= self.chunk_size:
            raise ValueError("chunk_overlap must be smaller than chunk_size.")

        try:
            self.llm = self.params["llm"]
        except KeyError:
            raise KeyError(
                "An 'llm' instance must be provided for MapReduceSummaryStrategy."
            )

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
        Loads chunks, and runs a Map-Reduce summary chain. The query is
        used to customize the prompts. This implementation includes an
        intermediate step to filter out irrelevant chunks before the reduce stage.
        The entire query process is subject to a timeout.
        """

        @timeout(self.query_timeout)
        def _query_with_timeout():
            if not load_path.exists():
                return "Error: Cached chunks not found."

            with open(load_path, "rb") as f:
                chunks = pickle.load(f)

            if not chunks:
                return "The document is empty."

            # 1. Map step - use LCEL instead of LLMChain
            map_chain = MAP_PROMPT | self.llm | StrOutputParser()

            # Process each chunk in parallel
            map_inputs = [{"text": chunk, "question": query} for chunk in chunks]
            map_results = map_chain.batch(
                map_inputs, config={"max_concurrency": self.max_concurrency}
            )

            # 2. Filter step
            # The prompt asks the LLM to return a specific string if no info is found.
            # We filter out those responses.
            summaries = [
                result
                for result in map_results
                if "does not contain any information" not in result.lower()
            ]

            if not summaries:
                return (
                    "The document does not contain information to answer the question."
                )

            # 3. Reduce step - use create_stuff_documents_chain
            # Convert summaries to Document objects for the reduce chain
            summary_docs = [Document(page_content=summary) for summary in summaries]

            # Create the reduce chain using create_stuff_documents_chain
            reduce_chain = create_stuff_documents_chain(
                self.llm, REDUCE_PROMPT, document_variable_name="context"
            )

            # Execute the reduce step
            result_dict = reduce_chain.invoke(
                {"context": summary_docs, "question": query}
            )

            # Since create_stuff_documents_chain returns the string directly
            return result_dict if isinstance(result_dict, str) else str(result_dict)

        try:
            return _query_with_timeout()
        except TimeoutError:
            return f"Map-reduce summary processing timed out after {self.query_timeout} seconds."
