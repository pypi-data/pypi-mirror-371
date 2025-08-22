# fairlib.modules.mal/local_llama_adapter.py
"""
This module provides a model adapter for connecting to local language models
served by the Ollama platform.

This adapter requires a running Ollama instance. To run a model, execute a
command in your terminal like: `ollama run llama3`

It also requires the 'httpx' library for async HTTP requests.
You can install it with: `pip install httpx`
"""
import asyncio
import json
from typing import List, Dict, Any, Generator, AsyncGenerator, Optional

from fairlib.core.interfaces.llm import AbstractChatModel
from fairlib.core.message import Message

# Guard for optional dependency
try:
    import httpx
    HTTPX_INSTALLED = True
except ImportError:
    HTTPX_INSTALLED = False


class OllamaAdapter(AbstractChatModel):
    """
    An adapter for interacting with local models via the Ollama API.

    This class handles communication with an Ollama server's '/api/chat'
    endpoint, supporting single-shot and streaming interactions in both a
    synchronous and asynchronous manner. It is designed to be a robust and
    performant component of the Model Abstraction Layer (MAL).
    """
    def __init__(self, model_name: str = "llama3", host: str = "http://localhost:11434"):
        """
        Initializes the OllamaAdapter.

        Args:
            model_name (str): The name of the model to use that is served by
                              Ollama (e.g., "llama3", "mistral").
            host (str): The URL of the running Ollama server.

        Raises:
            ImportError: If the 'httpx' library is not installed.
        """
        if not HTTPX_INSTALLED:
            raise ImportError(
                "The 'httpx' library is not installed. "
                "Please install it to use OllamaAdapter by running: pip install httpx"
            )
        self.model_name = model_name
        self.api_url = f"{host.strip('/')}/api/chat"
        self.client = httpx.AsyncClient(timeout=60.0)
        print(f"✅ OllamaAdapter initialized for model '{self.model_name}' at '{self.api_url}'")

    def _prepare_payload(self, messages: List[Message], stream: bool, **kwargs: Any) -> Dict[str, Any]:
        """Helper to create the JSON payload for the Ollama API."""
        # The Ollama API expects a list of dictionaries, not our Message objects.
        # We assume our Message objects have a to_dict() method or similar serialization.
        dict_messages = [{"role": msg.role, "content": msg.content} for msg in messages]
        
        return {
            "model": self.model_name,
            "messages": dict_messages,
            "stream": stream,
            "options": kwargs
        }

    async def ainvoke(self, messages: List[Message], **kwargs: Any) -> Message:
        """
        Makes a single, asynchronous call to the Ollama chat endpoint.
        """
        payload = self._prepare_payload(messages, stream=False, **kwargs)
        
        try:
            response = await self.client.post(self.api_url, json=payload)
            response.raise_for_status()  # Raise exception for 4xx/5xx errors
            
            response_data = response.json()
            assistant_message = response_data.get("message", {})
            
            return Message(
                role=assistant_message.get("role", "assistant"),
                content=assistant_message.get("content", "").strip()
            )
        except httpx.ConnectError as e:
            error_msg = f"Connection to Ollama server at {self.api_url} failed. Is Ollama running? Error: {e}"
            print(error_msg)
            return Message(role="assistant", content=error_msg)
        except httpx.HTTPStatusError as e:
            error_msg = f"Ollama API returned an error: {e.response.status_code} {e.response.text}"
            print(error_msg)
            return Message(role="assistant", content=error_msg)

    def invoke(self, messages: List[Message], **kwargs: Any) -> Message:
        """
        Makes a single, synchronous call by wrapping the async version.
        This is suitable for testing or scripts that are not fully async.
        """
        # This is a simple way to run an async method from a sync context.
        return asyncio.run(self.ainvoke(messages, **kwargs))

    async def astream(self, messages: List[Message], **kwargs: Any) -> AsyncGenerator[Message, None]:
        """
        Creates an asynchronous generator that streams chunks of the model's response.
        """
        payload = self._prepare_payload(messages, stream=True, **kwargs)
        
        try:
            async with self.client.stream("POST", self.api_url, json=payload) as response:
                response.raise_for_status()
                async for line in response.aiter_lines():
                    if line:
                        chunk = json.loads(line)
                        delta = chunk.get("message", {}).get("content", "")
                        if delta:
                            yield Message(role="assistant", content=delta)
        except httpx.ConnectError as e:
            error_msg = f"Connection to Ollama server at {self.api_url} failed during stream. Is Ollama running? Error: {e}"
            print(error_msg)
            yield Message(role="assistant", content=error_msg)
        except httpx.HTTPStatusError as e:
            error_msg = f"Ollama API returned an error during stream: {e.response.status_code} {e.response.text}"
            print(error_msg)
            yield Message(role="assistant", content=error_msg)

    def stream(self, messages: List[Message], **kwargs: Any) -> Generator[Message, None, None]:
        """
        Creates a synchronous generator by wrapping the async streamer.
        """
        async def get_chunks():
            async for chunk in self.astream(messages, **kwargs):
                yield chunk

        # This approach runs the async generator until it's exhausted.
        loop = asyncio.get_event_loop()
        gen = get_chunks()
        while True:
            try:
                yield loop.run_until_complete(gen.__anext__())
            except StopAsyncIteration:
                break

    def get_model_capabilities(self) -> Dict[str, Any]:
        """
        Returns a dictionary describing the capabilities of the model.
        """
        # Standard Ollama models do not support OpenAI-style function/tool calling.
        return {
            "function_calling": False,
            "tool_calling": False,
            "supports_streaming": True,
            "supports_async": True,
        }