# fairlib.utils.autograder_utils.py
"""
================================================================================
            Shared Utilities for the Multi-Agent Autograder Framework
================================================================================

**Purpose:**
This module contains shared, reusable components for both the essay and programming
autograders. By centralizing common logic, we make the overall framework more
modular, maintainable, and easier to extend. This approach prevents code
duplication and ensures that improvements to fairlib.core.functionalities benefit all
tools that use them.

**Components:**
- **RAG Knowledge Base Setup:** A function to create and populate a vector store
  from course materials, used for context-aware grading.
- **Pydantic Schemas:** Data models (`GradingCriterion`, `FinalGrade`) that
  provide a standardized, structured format for grading output, ensuring
  consistency.
- **Agent Factory:** A helper function (`create_agent`) to simplify the
  instantiation of agents, encapsulating their standard setup.
- **Reporting:** A function (`format_report`) to turn the final structured
  JSON grade into a human-readable text report.
"""
from __future__ import annotations

import json
import logging
from typing import List, Optional

from pydantic import BaseModel, Field, ValidationError

# Framework imports
from fairlib.core.types import Document
from fairlib.utils.document_processor import DocumentProcessor

from fairlib import (
    settings,
    SimpleAgent,
    ReActPlanner,
    ToolRegistry,
    ToolExecutor,
    SentenceTransformerEmbedder,
    ChromaDBVectorStore,
    LongTermMemory,
    SimpleRetriever,
    WorkingMemory,
)

# Chroma is optional; setup_knowledge_base will error if missing.
try:
    import chromadb
    _CHROMA_AVAILABLE = True
except Exception:
    chromadb = None
    _CHROMA_AVAILABLE = False

logger = logging.getLogger(__name__)


# ------------------------------------------------------------------------------
# RAG Knowledge Base Setup
# ------------------------------------------------------------------------------

def setup_knowledge_base(materials_path: str) -> Optional[LongTermMemory]:
    """
    Creates and populates a RAG knowledge base from course materials.
    This enables agents to perform fact-checking against course-specific context.
    This method uses the ChromaDB vector store defined in vector_store.py
    """
    if not _CHROMA_AVAILABLE or chromadb is None:
        logger.error("Cannot set up knowledge base because `chromadb` is not installed.")
        return None

    logger.info("Setting up course knowledge base from: %s", materials_path)
    try:
        # 1) Parse + chunk with DocumentProcessor
        dp = DocumentProcessor({"files_directory": materials_path})
        docs: List[Document] = dp.load_documents_from_folder(materials_path)
        if not docs:
            logger.warning("No course materials found to build knowledge base.")
            return None

        # 2) Embedder
        embedder = SentenceTransformerEmbedder()

        # 3) Chroma vector store (in-memory client by default)
        chroma_client = chromadb.Client()
        vector_store = ChromaDBVectorStore(
            client=chroma_client,
            collection_name="course_kb",
            embedder=embedder
        )

        # 4) Ingest Documents into Chroma
        texts = [d.page_content for d in docs]
        metadatas = [d.metadata for d in docs] if docs and hasattr(docs[0], "metadata") else None
        vector_store.add_documents(texts, metadatas=metadatas)

        # 5) Wrap in LongTermMemory
        long_term_memory = LongTermMemory(vector_store)
        logger.info("✅ Knowledge base created successfully with %d chunks.", len(docs))
        return long_term_memory

    except Exception as e:
        logger.error(f"Failed to set up knowledge base: {e}", exc_info=True)
        return None


# ------------------------------------------------------------------------------
# Pydantic Schemas for Standardized Grading
# ------------------------------------------------------------------------------

class GradingCriterion(BaseModel):
    """A Pydantic model for a single criterion in a grading rubric."""
    criterion: str = Field(..., description="The name of the grading criterion (e.g., 'Thesis Statement').")
    score: int = Field(..., description="The score awarded for this criterion (out of the max score).")
    max_score: int = Field(..., description="The maximum possible score for this criterion.")
    justification: str = Field(..., description="A detailed justification, citing specific examples.")

class FinalGrade(BaseModel):
    """The main Pydantic model representing the complete, structured grade for a submission."""
    graded_criteria: List[GradingCriterion] = Field(..., description="A list of all graded criteria.")
    overall_feedback: str = Field(..., description="A high-level summary of strengths and areas for improvement.")
    final_score: int = Field(..., description="The sum of all scores from the graded criteria.")


# ------------------------------------------------------------------------------
# Agent Factory
# ------------------------------------------------------------------------------

def create_agent(llm, role_description, tools=None):
    """
    Helper factory to simplify agent creation.
    Encapsulates the standard setup for a SimpleAgent, ensuring consistency.
    """
    tool_registry = ToolRegistry()
    if tools:
        for tool in tools:
            tool_registry.register_tool(tool)

    planner = ReActPlanner(llm, tool_registry)
    executor = ToolExecutor(tool_registry) if tools else None
    memory = WorkingMemory()

    agent = SimpleAgent(llm, planner, executor, memory)
    agent.role_description = role_description
    return agent


# ------------------------------------------------------------------------------
# Reporting Utility
# ------------------------------------------------------------------------------

def format_report(grade_json_str: str, filename: str) -> str:
    """Formats the final JSON grade into a human-readable report."""
    try:
        raw_data = json.loads(grade_json_str)

        if "error" in raw_data:
            return f"GRADE REPORT FOR: {filename}\n\n[ERROR]\n{raw_data['error']}"

        data: FinalGrade = FinalGrade.model_validate_json(grade_json_str)

        report_lines = [f"GRADE REPORT FOR: {filename}\n", "=" * 40]

        total_max_score = sum(item.max_score for item in data.graded_criteria)
        final_score = data.final_score

        report_lines.append(f"FINAL SCORE: {final_score} / {total_max_score}\n")
        report_lines.append("**Overall Feedback:**")
        report_lines.append(data.overall_feedback)
        report_lines.append("\n**Rubric Breakdown:**")

        for item in data.graded_criteria:
            report_lines.append(f"- {item.criterion} ({item.score}/{item.max_score}): {item.justification.strip()}")

        return "\n".join(report_lines)

    except ValidationError as e:
        logger.error(
            f"Could not validate the final JSON evaluation against schema for {filename}. "
            f"Error: {e}. Raw output:\n{grade_json_str}"
        )
        return (
            f"GRADE REPORT FOR: {filename}\n\n[ERROR]\n"
            f"Could not validate the final AI evaluation against the expected format. Details: {e}\n\n"
            f"Raw Output:\n{grade_json_str}"
        )
    except (json.JSONDecodeError, TypeError) as e:
        logger.error(
            f"Could not parse the final JSON evaluation for {filename}. Error: {e}. Raw output:\n{grade_json_str}"
        )
        return (
            f"GRADE REPORT FOR: {filename}\n\n[ERROR]\n"
            f"Could not parse the final AI evaluation. Details: {e}\n\n"
            f"Raw Output:\n{grade_json_str}"
        )
