# fairlib.core.interfaces/llm.py
"""
This module defines the abstract interfaces for language models.

The framework supports two primary types of language model interactions, each
represented by its own abstract base class:
1.  `AbstractLanguageModel`: For simpler text-completion models (text-in, text-out).
2.  `AbstractChatModel`: For more sophisticated chat-based models that operate on a
    structured list of messages. This is the primary interface used for agentic workflows.

These contracts ensure that any language model can be seamlessly integrated into the
framework's Model Abstraction Layer (MAL).
"""

import abc
from typing import Any, List, Dict, Generator, AsyncGenerator
from ..message import Message

class AbstractLanguageModel(abc.ABC):
    """
    An abstract interface for a standard text-completion language model.

    This interface is best suited for models that take a single string prompt
    and return a single string completion.
    """
    @abc.abstractmethod
    def invoke(self, prompt: str, **kwargs: Any) -> str:
        """Makes a single, synchronous call to the language model."""
        ...

    @abc.abstractmethod
    async def ainvoke(self, prompt: str, **kwargs: Any) -> str:
        """Makes a single, asynchronous call to the language model."""
        ...

    @abc.abstractmethod
    def stream(self, prompt: str, **kwargs: Any) -> Generator[str, None, None]:
        """
        Creates a synchronous generator that streams chunks of the model's response.
        """
        ...

    @abc.abstractmethod
    async def astream(self, prompt: str, **kwargs: Any) -> AsyncGenerator[str, None]:
        """
        Creates an asynchronous generator that streams chunks of the model's response.
        """
        ...


class AbstractChatModel(abc.ABC):
    """
    An abstract interface for a chat-based language model.

    This is the primary and more powerful interface used for building agents.
    It operates on a list of `Message` objects, allowing it to understand
    conversational history and roles (system, user, assistant, tool).
    """
    @abc.abstractmethod
    def invoke(self, messages: List[Message], **kwargs: Any) -> Message:
        """
        Makes a single, synchronous call to the chat model with a list of messages.

        Args:
            messages: A list of `Message` objects representing the conversation.
            **kwargs: Provider-specific options, e.g., `temperature`, `top_p`.

        Returns:
            A single `Message` object containing the assistant's complete response.
        """
        ...

    @abc.abstractmethod
    async def ainvoke(self, messages: List[Message], **kwargs: Any) -> Message:
        """
        Makes a single, asynchronous call to the chat model with a list of messages.
        
        Args:
            messages: A list of `Message` objects representing the conversation.
            **kwargs: Provider-specific options.

        Returns:
            A single `Message` object containing the assistant's complete response.
        """
        ...

    @abc.abstractmethod
    def stream(self, messages: List[Message], **kwargs: Any) -> Generator[Message, None, None]:
        """
        Creates a synchronous generator that streams chunks of the model's response.

        Each yielded item should be a `Message` object, allowing the content to be
        built up incrementally.

        Args:
            messages: A list of `Message` objects representing the conversation.
            **kwargs: Provider-specific options.

        Yields:
            `Message` objects representing chunks of the response.
        """
        ...

    @abc.abstractmethod
    async def astream(self, messages: List[Message], **kwargs: Any) -> AsyncGenerator[Message, None]:
        """
        Creates an asynchronous generator that streams chunks of the model's response.

        Args:
            messages: A list of `Message` objects representing the conversation.
            **kwargs: Provider-specific options.

        Yields:
            `Message` objects representing chunks of the response.
        """
        ...

    @abc.abstractmethod
    def get_model_capabilities(self) -> Dict[str, Any]:
        """
        Returns a dictionary describing the capabilities of the model.

        This allows the framework to introspect the model and understand its features,
        such as whether it supports function calling, tool use, or other specific
        structured outputs.

        Example:
            return {"function_calling": True, "tool_calling": False}
        """
        ...

        # --- The `chat` method can now be a simple wrapper around `invoke` ---
    def chat(self, messages: List[Message], temperature: float = 0.7) -> str:
        """A simplified chat method for convenience, consistent with our demos."""
        response_message = self.invoke(messages, temperature=temperature)
        return response_message.content