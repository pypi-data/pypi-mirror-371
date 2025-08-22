# fairlib.modules.perception/echo_preprocessor.py
"""
This module provides a basic, pass-through implementation of the AbstractPerception
interface.
"""
from typing import Any
from fairlib.core.interfaces.perception import AbstractPerception

class EchoPreprocessor(AbstractPerception):
    """
    An implementation of AbstractPerception that performs no operations on the
    input data. It simply returns the input exactly as it was received.

    This class serves as a default or placeholder perception component for agents
    that do not require any special input processing or for testing purposes.
    """
    def process_input(self, raw_input: Any, **kwargs: Any) -> Any:
        """
        Synchronously "processes" the input by returning it unmodified.

        Args:
            raw_input: The raw data from the environment.
            **kwargs: Ignored. Included for interface compatibility.

        Returns:
            The original, unaltered `raw_input`.
        """
        # This implementation is a simple pass-through.
        return raw_input

    async def aprocess_input(self, raw_input: Any, **kwargs: Any) -> Any:
        """
        Asynchronously "processes" the input by returning it unmodified.

        Args:
            raw_input: The raw data from the environment.
            **kwargs: Ignored. Included for interface compatibility.

        Returns:
            The original, unaltered `raw_input`.
        """
        # As this is a non-blocking operation, the async method can also
        # directly return the input.
        return raw_input