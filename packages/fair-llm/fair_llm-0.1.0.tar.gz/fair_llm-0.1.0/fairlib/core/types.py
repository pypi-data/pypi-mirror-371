# fairlib.core.types.py
"""
This module defines fundamental, general-purpose data structures for the framework.

These types are not specific to the agent's internal messaging system (which is
defined in `core/message.py`) but are used across various capabilities, such as
the data representation for Retrieval-Augmented Generation (RAG).
"""

from typing import Optional, Dict, Any, List
from pydantic import BaseModel, Field

class Document:
    """
    Represents a single chunk of text content, typically used as context for
    Retrieval-Augmented Generation (RAG) pipelines.

    An external piece of knowledge, like a PDF or a text file, is often split
    into multiple `Document` objects for easier processing and retrieval.

    Attributes:
        page_content (str): The actual text content of the document chunk.
        metadata (dict): A dictionary holding arbitrary metadata associated with
                         the content, such as the source file, page number, or
                         other identifiers.
    """
    def __init__(self, page_content: str, metadata: Optional[Dict[str, Any]] = None):
        """
        Initializes a Document object.

        Args:
            page_content: The string content of the document.
            metadata: An optional dictionary of metadata. If None is provided,
                      it defaults to an empty dictionary.
        """
        # The main text content of the document.
        self.page_content = page_content

        # This idiom ensures that self.metadata is always a dictionary,
        # preventing errors if metadata is not provided.
        self.metadata = metadata or {}

    def __str__(self) -> str:
        """
        Provides a concise string representation of the Document object,
        useful for logging and debugging.
        """
        # Truncates the page_content to the first 50 characters for readability.
        return f"Document(content='{self.page_content[:50]}...', metadata={self.metadata})"

# --- Pydantic Schemas for Standardized Grading ---
# These models enforce a consistent, structured output from the grading agents.
# They are defined here as they are fairlib.core.data types for the autograder tools.

class GradingCriterion(BaseModel):
    """A Pydantic model for a single criterion in a grading rubric."""
    criterion: str = Field(..., description="The name of the grading criterion (e.g., 'Thesis Statement', 'Code Correctness').")
    score: int = Field(..., description="The score awarded for this criterion (out of the max score).")
    max_score: int = Field(..., description="The maximum possible score for this criterion.")
    justification: str = Field(..., description="A detailed justification for the score, citing specific examples from the submission.")

class FinalGrade(BaseModel):
    """The main Pydantic model representing the complete, structured grade for a submission."""
    graded_criteria: List[GradingCriterion] = Field(..., description="A list of all graded criteria from the rubric.")
    overall_feedback: str = Field(..., description="A high-level summary of the submission's strengths and areas for improvement.")
    final_score: int = Field(..., description="The sum of all scores from the graded criteria.")
