# fairlib.modules.perception/text_parser.py
"""
This module provides a foundational perception component for cleaning and
normalizing raw text input.
"""
from typing import Any
from fairlib.core.interfaces.perception import AbstractPerception

class TextParser(AbstractPerception):
    """
    A perception module that normalizes raw text input.

    This class serves as a basic but robust first step in a data processing
    pipeline. It ensures that text is in a consistent format (e.g., lowercase,
    no leading/trailing whitespace) before being passed to other parts of the
    agent, such as the planner or a RAG pipeline.
    """
    def __init__(self, do_strip: bool = True, do_lowercase: bool = True):
        """
        Initializes the TextParser with specific normalization rules.

        Args:
            do_strip: If True, removes leading and trailing whitespace.
            do_lowercase: If True, converts the entire text to lowercase.
        """
        self.do_strip = do_strip
        self.do_lowercase = do_lowercase
        print("✅ TextParser initialized.")

    def process_input(self, raw_input: Any, **kwargs: Any) -> str:
        """
        Synchronously normalizes the raw input text.

        This method applies a series of cleaning steps to the input string based
        on the instance's configuration. It is designed to be robust against
        non-string inputs.

        Args:
            raw_input: The raw data to be processed.
            **kwargs: Ignored. Included for interface compatibility.

        Returns:
            A normalized string.
        """
        # --- Robustness Check ---
        # Ensure the input is a string before processing. If not, convert it.
        if not isinstance(raw_input, str):
            processed_input = str(raw_input)
        else:
            processed_input = raw_input

        # --- Normalization Steps ---
        # Apply stripping and lowercasing based on the configuration.
        if self.do_strip:
            processed_input = processed_input.strip()
        if self.do_lowercase:
            processed_input = processed_input.lower()

        return processed_input

    async def aprocess_input(self, raw_input: Any, **kwargs: Any) -> str:
        """
        Asynchronously normalizes the raw input text.

        As text normalization is a fast, CPU-bound operation, this method
        directly calls the synchronous `process_input` method.

        Args:
            raw_input: The raw data to be processed.
            **kwargs: Ignored. Included for interface compatibility.

        Returns:
            A normalized string.
        """
        # Since the operation is not I/O-bound, we can call the sync version directly.
        return self.process_input(raw_input, **kwargs)