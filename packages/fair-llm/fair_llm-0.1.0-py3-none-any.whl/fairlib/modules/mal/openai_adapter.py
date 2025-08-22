# fairlib.modules.mal/openai_adapter.py
"""
This module provides a robust, asynchronous-first adapter for interacting with
OpenAI's chat completion models, conforming to the AbstractChatModel interface.
"""
import os
from typing import List, Dict, Any, AsyncIterator, Iterator, Optional

# Guard for optional dependency
try:
    import openai
    from openai import OpenAI, AsyncOpenAI
    OPENAI_INSTALLED = True
except ImportError:
    OPENAI_INSTALLED = False

from fairlib.core.interfaces.llm import AbstractChatModel
from fairlib.core.message import Message

class OpenAIAdapter(AbstractChatModel):
    """
    An adapter for interacting with OpenAI's chat models.

    This class provides a robust, async-first implementation of the
    AbstractChatModel interface. It uses the official OpenAI Python library
    and handles both synchronous and asynchronous operations for chat,
    streaming, and function/tool calling.
    """
    def __init__(self, api_key: Optional[str] = None, model_name: str = "gpt-4o"):
        """
        Initializes the OpenAIAdapter.

        Args:
            api_key (Optional[str]): Your OpenAI API key. If not provided, it
                                     will be read from the OPENAI_API_KEY
                                     environment variable.
            model_name (str): The name of the OpenAI model to use.

        Raises:
            ImportError: If the 'openai' library is not installed.
            ValueError: If the API key is not provided either directly or as
                        an environment variable.
        """
        if not OPENAI_INSTALLED:
            raise ImportError(
                "The 'openai' library is not installed. "
                "Please install it with `pip install openai` to use this adapter."
            )
        
        # Resolve API key from argument or environment variable
        resolved_api_key = api_key or os.getenv("OPENAI_API_KEY")
        if not resolved_api_key:
            raise ValueError("OpenAI API key not found. Please provide it directly or set the OPENAI_API_KEY environment variable.")

        # Initialize both sync and async clients for their respective methods
        self.sync_client = OpenAI(api_key=resolved_api_key)
        self.async_client = AsyncOpenAI(api_key=resolved_api_key)
        self.model_name = model_name

    def _prepare_messages(self, messages: List[Message]) -> List[Dict[str, Any]]:
        """
        Helper to convert the framework's Message objects to the dictionary
        format required by the OpenAI API.
        """
        prepared_messages = []
        for msg in messages:
            msg_dict = {"role": msg.role, "content": msg.content or ""}
            # Add optional fields only if they are present in the source message
            if msg.name:
                msg_dict["name"] = msg.name
            
            # If the message from our history has tool_calls, include them.
            if msg.tool_calls:
                msg_dict["tool_calls"] = msg.tool_calls
            
            if msg.tool_call_id:
                msg_dict["tool_call_id"] = msg.tool_call_id
                
            prepared_messages.append(msg_dict)
        return prepared_messages

    def invoke(self, messages: List[Message], **kwargs: Any) -> Message:
        """
        Synchronously invokes the model to get a single response.
        """
        openai_messages = self._prepare_messages(messages)
        try:
            response = self.sync_client.chat.completions.create(
                model=self.model_name,
                messages=openai_messages,
                **kwargs
            )
            response_message = response.choices[0].message
            # Convert the OpenAI response message back to our framework's Message object
            return Message(
                role="assistant",
                content=response_message.content,
                tool_calls=response_message.tool_calls
            )
        except Exception as e:
            print(f"An error occurred with the OpenAI API (invoke): {e}")
            return Message(role="assistant", content=f"Error: {e}")

    async def ainvoke(self, messages: List[Message], **kwargs: Any) -> Message:
        """
        Asynchronously invokes the model using a true async client.
        """

        # NOTE: Ensure we properly format conversation history (context), 
        #       ie.e, prompt for use with the openai API
        openai_messages = self._prepare_messages(messages)
       
        try:
            response = await self.async_client.chat.completions.create(
                model=self.model_name,
                messages=openai_messages,
                **kwargs
            )
            response_message = response.choices[0].message
            return Message(
                role="assistant",
                content=response_message.content,
                tool_calls=response_message.tool_calls
            )
        except Exception as e:
            print(f"An error occurred with the OpenAI API (ainvoke): {e}")
            return Message(role="assistant", content=f"Error: {e}")

    def stream(self, messages: List[Message], **kwargs: Any) -> Iterator[Message]:
        """
        Streams the model's response chunk by chunk synchronously.
        """
        openai_messages = self._prepare_messages(messages)
        try:
            stream = self.sync_client.chat.completions.create(
                model=self.model_name,
                messages=openai_messages,
                stream=True,
                **kwargs
            )
            for chunk in stream:
                delta = chunk.choices[0].delta
                if delta and delta.content:
                    yield Message(role="assistant", content=delta.content)
        except Exception as e:
            print(f"An error occurred with the OpenAI API (stream): {e}")
            yield Message(role="assistant", content=f"Error: {e}")

    async def astream(self, messages: List[Message], **kwargs: Any) -> AsyncIterator[Message]:
        """
        Asynchronously streams the model's response chunk by chunk.
        """
        openai_messages = self._prepare_messages(messages)
        try:
            stream = await self.async_client.chat.completions.create(
                model=self.model_name,
                messages=openai_messages,
                stream=True,
                **kwargs
            )
            async for chunk in stream:
                delta = chunk.choices[0].delta
                if delta and delta.content:
                    yield Message(role="assistant", content=delta.content)
        except Exception as e:
            print(f"An error occurred with the OpenAI API (astream): {e}")
            yield Message(role="assistant", content=f"Error: {e}")

    def get_model_capabilities(self) -> Dict[str, Any]:
        """
        Returns a dictionary of the model's known capabilities.
        """
        return {
            "supports_streaming": True,
            "supports_async": True,
            "supports_tool_calling": True,
            "max_context_window": 128000, # Example for gpt-4-turbo
        }