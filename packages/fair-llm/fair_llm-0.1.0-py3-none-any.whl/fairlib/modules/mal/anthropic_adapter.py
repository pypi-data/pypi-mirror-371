# mal/anthropic_adapter.py
"""
This module provides a robust, asynchronous-first adapter for interacting with
Anthropic's Claude models, conforming to the AbstractChatModel interface.
"""
import asyncio
import os
from typing import List, Dict, Any, Iterator, AsyncIterator, Tuple, Optional

# Guard for optional dependency
try:
    import anthropic
    from anthropic import Anthropic, AsyncAnthropic
    ANTHROPIC_INSTALLED = True
except ImportError:
    ANTHROPIC_INSTALLED = False

from fairlib.core.interfaces.llm import AbstractChatModel
from fairlib.core.message import Message

class AnthropicAdapter(AbstractChatModel):
    """
    An adapter for interacting with Anthropic's Claude models.

    This class provides a robust, async-first implementation of the
    AbstractChatModel interface. It uses the official Anthropic Python library
    and correctly handles the separation of the system prompt for optimal
    performance with Claude models.
    """
    def __init__(self, api_key: Optional[str] = None, model_name: str = "claude-3-opus-20240229"):
        """
        Initializes the AnthropicAdapter.

        Args:
            api_key (Optional[str]): Your Anthropic API key. If not provided,
                                     it will be read from the ANTHROPIC_API_KEY
                                     environment variable.
            model_name (str): The name of the Anthropic model to use.

        Raises:
            ImportError: If the 'anthropic' library is not installed.
            ValueError: If the API key is not provided either directly or as
                        an environment variable.
        """
        if not ANTHROPIC_INSTALLED:
            raise ImportError(
                "The 'anthropic' library is not installed. "
                "Please install it with `pip install anthropic` to use this adapter."
            )

        resolved_api_key = api_key or os.getenv("ANTHROPIC_API_KEY")
        if not resolved_api_key:
            raise ValueError("Anthropic API key not found. Please provide it directly or set the ANTHROPIC_API_KEY environment variable.")

        # Initialize both clients for sync and async methods
        self.sync_client = Anthropic(api_key=resolved_api_key)
        self.async_client = AsyncAnthropic(api_key=resolved_api_key)
        self.model_name = model_name

    def _prepare_messages(self, messages: List[Message]) -> Tuple[str, List[Dict[str, Any]]]:
        """
        Helper to convert framework messages to Anthropic's format.

        Anthropic's API requires the system prompt to be a separate, top-level
        parameter rather than part of the messages list. This method handles
        that separation.

        Returns:
            A tuple containing the system prompt string and the list of user/assistant
            messages.
        """
        system_prompt = ""
        if messages and messages[0].role == "system":
            # Extract the system prompt and remove it from the message list
            system_prompt = messages[0].content
            messages = messages[1:]
        
        # Convert the remaining Message objects to the required dictionary format.
        anthropic_messages = [{"role": msg.role, "content": msg.content} for msg in messages]
        return system_prompt, anthropic_messages

    async def ainvoke(self, messages: List[Message], **kwargs: Any) -> Message:
        """
        Asynchronously invokes the model to get a single response.
        """
        system_prompt, anthropic_messages = self._prepare_messages(messages)
        try:
            # Use the async client for a non-blocking API call
            response = await self.async_client.messages.create(
                model=self.model_name,
                system=system_prompt,
                messages=anthropic_messages,
                max_tokens=kwargs.get("max_tokens", 2048),
                **kwargs
            )
            # The main content is in the first block of the response content list
            content = response.content[0].text
            return Message(role="assistant", content=content)
        except anthropic.APIError as e:
            error_msg = f"An error occurred with the Anthropic API (ainvoke): {e}"
            print(error_msg)
            return Message(role="assistant", content=error_msg)

    def invoke(self, messages: List[Message], **kwargs: Any) -> Message:
        """
        Synchronously invokes the model by running the async version.
        """
        return asyncio.run(self.ainvoke(messages, **kwargs))

    async def astream(self, messages: List[Message], **kwargs: Any) -> AsyncIterator[Message]:
        """
        Asynchronously streams the model's response chunk by chunk.
        """
        system_prompt, anthropic_messages = self._prepare_messages(messages)
        try:
            # Use the async client's streaming context manager
            async with self.async_client.messages.stream(
                model=self.model_name,
                system=system_prompt,
                messages=anthropic_messages,
                max_tokens=kwargs.get("max_tokens", 2048),
                **kwargs
            ) as stream:
                # Asynchronously iterate over the text chunks
                async for text in stream.text_stream:
                    yield Message(role="assistant", content=text)
        except anthropic.APIError as e:
            error_msg = f"An error occurred with the Anthropic API (astream): {e}"
            print(error_msg)
            yield Message(role="assistant", content=error_msg)

    def stream(self, messages: List[Message], **kwargs: Any) -> Iterator[Message]:
        """
        Synchronously streams the model's response by wrapping the async streamer.
        """
        async def get_chunks():
            async for chunk in self.astream(messages, **kwargs):
                yield chunk

        loop = asyncio.get_event_loop()
        gen = get_chunks()
        while True:
            try:
                yield loop.run_until_complete(gen.__anext__())
            except StopAsyncIteration:
                break

    def get_model_capabilities(self) -> Dict[str, Any]:
        """
        Returns a dictionary of the model's known capabilities.
        """
        return {
            "supports_streaming": True,
            "supports_async": True,
            "supports_system_prompt": True,
            "max_context_window": 200000, # Example for claude-3-opus
        }

    # The 'chat' method from the base class is often sufficient, but providing
    # a concrete implementation here ensures it uses the adapter's logic correctly.
    def chat(self, messages: List[Message], temperature: float = 0.7) -> str:
        """A simplified chat method for convenience."""
        response_message = self.invoke(messages, temperature=temperature)
        return response_message.content