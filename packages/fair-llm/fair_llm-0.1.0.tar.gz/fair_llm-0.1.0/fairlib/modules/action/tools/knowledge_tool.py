# fairlib.modules.action/tools/knowledge_tool.py
"""
================================================================================
                        Knowledge Base Query Tool (RAG)
================================================================================

**Purpose:**
This module provides a specialized tool that allows an agent to perform
Retrieval-Augmented Generation (RAG) queries against a pre-built knowledge
base (vector store).

**How it Works:**
The `KnowledgeBaseQueryTool` takes a natural language query (e.g., a claim
from a student's essay) and uses a `SimpleRetriever` instance to find the most
semantically similar text chunks from the course materials. It then formats
these findings into a clear "Observation" for the calling agent to use in its
reasoning process.

This tool is the key component that enables the `FactChecker` agent.
"""
import logging
from fairlib import AbstractTool, SimpleRetriever
from fairlib.core.types import Document

# Configure a logger for this specific module
logger = logging.getLogger(__name__)

class KnowledgeBaseQueryTool(AbstractTool):
    """
    A tool that allows an agent to query a RAG knowledge base to find
    relevant context or verify claims.
    """
    # The name the agent will use to call this tool.
    name = "course_knowledge_query"
    # The description helps the agent's planner understand when to use this tool.
    description = "Queries course materials to verify claims or find information relevant to a topic."
    
    def __init__(self, retriever: SimpleRetriever): # TODO:: SHOULD THIS ACCEPT THE ABSTRACT CLASS CONTRACT? NOT THE SIMLE RETRIEVER?
        """
        Initializes the tool with a retriever instance. The retriever is the
        component that directly communicates with the vector store.
        
        Args:
            retriever: An initialized SimpleRetriever object.
        """
        self.retriever = retriever
    
    def use(self, tool_input: str) -> str:
        """
        Executes the RAG query against the knowledge base.

        Args:
            tool_input: The natural language query or claim to be verified.

        Returns:
            A formatted string containing the retrieved information, or a
            message indicating that no relevant information was found.
        """
        logger.info(f"Querying knowledge base for: '{tool_input}'")
        try:
            results = self.retriever.retrieve(query=tool_input, top_k=2)

            if not results:
                return "Observation: No relevant information was found in the knowledge base for this query."

            # Normalize results to strings for consistent formatting
            normalized_chunks = []
            for item in results:
                if isinstance(item, str):
                    normalized_chunks.append(item)
                elif isinstance(item, Document):
                    normalized_chunks.append(item.page_content or "")
                else:
                    normalized_chunks.append(str(item))

            formatted_results = "\n---\n".join(normalized_chunks)
            return f"Observation: The following information was found:\n{formatted_results}"

        except Exception as e:
            logger.error(f"RAG retrieval error: {e}", exc_info=True)
            return "Error: Could not query the knowledge base due to an internal error."
