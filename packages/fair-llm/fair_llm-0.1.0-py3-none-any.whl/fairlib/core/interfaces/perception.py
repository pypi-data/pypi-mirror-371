# fairlib.core.interfaces/perception.py
"""
This module defines the abstract interface for an agent's Perception system.

In an agent's cognitive architecture, Perception is the initial stage that
deals with raw input from the environment. It is responsible for taking
unstructured or semi-structured data and transforming it into a clean, usable
format that the agent's planning and reasoning components can work with.
"""

import abc
from typing import Any

class AbstractPerception(abc.ABC):
    """
    An abstract interface for a class that processes raw input data.

    A concrete implementation of this class might perform tasks such as:
    - Cleaning and normalizing raw user text.
    - Extracting structured data from an unstructured string.
    - Processing multimodal input (e.g., images, audio) into a format the
      language model can understand.
    - Applying initial security checks or validations.
    """
    @abc.abstractmethod
    def process_input(self, raw_input: Any, **kwargs) -> Any:
        """
        Synchronously processes raw input data into a structured format.

        Args:
            raw_input: The raw data from the environment, e.g., a user's text
                       query, data from a sensor, etc. Typed as `Any` for
                       maximum flexibility.
            **kwargs: Placeholder for additional implementation-specific arguments.

        Returns:
            The processed, structured data ready for the next stage of the
            agent's reasoning cycle.
        """
        ...

    @abc.abstractmethod
    async def aprocess_input(self, raw_input: Any, **kwargs) -> Any:
        """
        Asynchronously processes raw input data into a structured format.

        This is the asynchronous version of `process_input` and should be
        preferred in asyncio applications.

        Args:
            raw_input: The raw data from the environment.
            **kwargs: Placeholder for additional implementation-specific arguments.

        Returns:
            The processed, structured data.
        """
        ...