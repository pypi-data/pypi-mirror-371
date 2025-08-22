# fairlib.modules.mal/huggingface_adapter.py

"""
huggingface_adapter_fully_documented.py

A flexible adapter for running local Hugging Face transformer models as chat agents.
This module supports full precision and quantized models (via bitsandbytes),
streaming output, and CLI interaction. It wraps HuggingFace's transformers pipeline
into an interface that is agent-ready.

This module also includes:
- A CLI tool for interactive conversation with a model
- Alias-based model lookup
- Proper prompt formatting for chat models (with fallback)
"""

# Note: huggingface read token: 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

import asyncio
import sys
import argparse
import os
from typing import List, Dict, Any, AsyncIterator, Iterator, Optional

# Import critical dependencies, detect install state
try:
    import torch
    TORCH_INSTALLED = True
except ImportError:
    TORCH_INSTALLED = False

try:
    from transformers import (
        AutoModelForCausalLM,
        AutoTokenizer,
        TextStreamer,
        pipeline,
        BitsAndBytesConfig
    )
    TRANSFORMERS_INSTALLED = True
except ImportError:
    TRANSFORMERS_INSTALLED = False

from fairlib.core.interfaces.llm import AbstractChatModel
from fairlib.core.message import Message


TOKEN = "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"

# Optional aliases for popular models
MODEL_REGISTRY = {

    # --- Dolphin Models ---
    "dolphin3-llama32-3b": "cognitivecomputations/Dolphin3.0-Llama3.2-3B",
    "dolphin3-llama31-8b": "cognitivecomputations/Dolphin3.0-Llama3.1-8B",
    "dolphin3-qwen25-0.5b": "cognitivecomputations/Dolphin3.0-Qwen2.5-0.5B",
    "dolphin3-qwen25-3b": "cognitivecomputations/Dolphin3.0-Qwen2.5-3b",
    "dolphin27-mixtral-8x7b": "cognitivecomputations/dolphin-2.7-mixtral-8x7b",

    # --- Mistral / Mixtral ---
    "mistral-7b": "mistralai/Mistral-7B-Instruct-v0.1",
    "mistral-8b": "mistralai/Ministral-8B-Instruct-2410",
    "openhermes": "teknium/OpenHermes-2.5-Mistral-7B",
    "nous": "NousResearch/Nous-Hermes-2-Mixtral-8x7B-DPO",

    # --- Tiny and Fast Models ---
    "tinyllama": "TinyLlama/TinyLlama-1.1B-Chat-v1.0",
    "phi": "microsoft/phi-2",
    "phi4-mini-r": "microsoft/Phi-4-mini-reasoning",
    
    # --- LLaMA 2 and 3 ---
    "llama2-7b": "meta-llama/Llama-2-7b-chat-hf",
    "llama2-13b": "meta-llama/Llama-2-13b-chat-hf",
    "llama3-8b": "meta-llama/Meta-Llama-3-8B-Instruct",
    "llama3-70b": "meta-llama/Llama-3.3-70B-Instruct",

    # --- Zephyr / RedPajama / DeepSeek ---
    "zephyr": "HuggingFaceH4/zephyr-7b-beta",
    "redpajama": "togethercomputer/RedPajama-INCITE-Chat-3B-v1",
    "deepseek-coder": "deepseek-ai/deepseek-coder-6.7b-instruct",

    # --- Reka R1 Family ---
    "reka-r1": "reka-ai/R1",
    "reka-mini": "reka-ai/R1-Mini",

    # --- Other Good Models ---
    "openchat": "openchat/openchat-3.5-1210",
    "gemma": "google/gemma-7b-it",
}


class HuggingFaceAdapter(AbstractChatModel):
    """
    Adapter for HuggingFace transformer models used in chat-style interactions.
    """
    def __init__(self, model_name: str = "dolphin3-llama32-3b", 
                 quantized: bool = False, stream: bool = False, 
                 auth_token: Optional[str] = None, **kwargs):
        
        self.model_name = MODEL_REGISTRY.get(model_name.lower(), model_name)
        self.verbose = kwargs.pop("verbose", True)
        self.enable_streaming = stream
        
        self.auth_token = auth_token or os.getenv("HUGGING_FACE_HUB_TOKEN") or TOKEN

        if not TORCH_INSTALLED or not TRANSFORMERS_INSTALLED:
            raise ImportError("This adapter requires both 'torch' and 'transformers' libraries.")

        if self.verbose:
            print(f"🔧 Loading HuggingFace model: {self.model_name} (quantized={quantized}, stream={stream})")

        loading_args = {"token": self.auth_token} if self.auth_token else {}

        self.tokenizer = AutoTokenizer.from_pretrained(self.model_name, **loading_args)

        torch_dtype = kwargs.pop("torch_dtype", torch.float16)
        device_map = kwargs.pop("device_map", "auto")

        if quantized:
            quant_config = BitsAndBytesConfig(load_in_4bit=True, bnb_4bit_compute_dtype=torch_dtype)
            self.model = AutoModelForCausalLM.from_pretrained(
                self.model_name,
                device_map=device_map,
                quantization_config=quant_config,
                **loading_args
            )
        else:
            self.model = AutoModelForCausalLM.from_pretrained(
                self.model_name,
                torch_dtype=torch_dtype,
                device_map=device_map,
                **loading_args
            )

        self.default_gen_kwargs = {
            "max_new_tokens": kwargs.pop("max_new_tokens", 256),
            "temperature": kwargs.pop("temperature", 0.7),
            "top_p": kwargs.pop("top_p", 0.9),
            "do_sample": True
        }

        if self.enable_streaming:
            self.streamer = TextStreamer(self.tokenizer, skip_prompt=True)
            self.default_gen_kwargs["streamer"] = self.streamer
        else:
            self.streamer = None

        self.generator = pipeline("text-generation", model=self.model, tokenizer=self.tokenizer, **kwargs)

    def invoke(self, messages: List[Message], **kwargs) -> Message:
        """
        Synchronously generates a chat response given message history.
        This version builds a single prompt string using the tokenizer's chat
        template, which is a robust method.
        """
        # This calls the private helper method, which now returns a string.
        prompt_string = self._format_prompt(messages)
        
        generation_args = {**self.default_gen_kwargs, **kwargs}
        
        # Pass the single formatted prompt string to the generator pipeline.
        result = self.generator(prompt_string, **generation_args)
        
        # Slice the original prompt from the beginning of the result to get
        # only the newly generated text.
        assistant_reply = result[0]['generated_text'][len(prompt_string):].strip()
        
        return Message(role="assistant", content=assistant_reply)

    async def ainvoke(self, messages: List[Message], **kwargs) -> Message:
        """Async version of invoke, using a background thread."""
        return await asyncio.to_thread(self.invoke, messages, **kwargs)

    def stream(self, messages: List[Message], **kwargs) -> Iterator[Message]:
        """Initiates a streamed chat response. Output is streamed directly to console."""
        if not self.enable_streaming or not self.streamer:
            raise NotImplementedError("Streaming not enabled for this instance")
        
        full_response = self.invoke(messages, **kwargs)
        yield full_response

    async def astream(self, messages: List[Message], **kwargs) -> AsyncIterator[Message]:
        """Async streaming fallback."""
        if not self.enable_streaming:
            raise NotImplementedError("Streaming not enabled for this instance")
        
        result = await self.ainvoke(messages, **kwargs)
        yield result

    def _format_prompt(self, messages: List[Message]) -> str:
        """
        Formats a list of Message objects into a single, correctly formatted
        prompt string using the tokenizer's chat template.
        """
        # This logic is restored from the original version you provided,
        # ensuring compatibility and correctness.
        try:
            # The 'to_dict()' method should be available on your Message class
            chat_history = [msg.to_dict() for msg in messages]

            # NOTE: Here is where the prompt is properly formatted 
            #       for the specific model currently in use.
            templated = self.tokenizer.apply_chat_template(chat_history, 
                                                           tokenize=False, 
                                                           add_generation_prompt=True)
            return templated
        
        except Exception:
            # Fallback for models without a chat template
            return "\n".join(f"{msg.role}: {msg.content}" for msg in messages)

    def get_model_capabilities(self) -> Dict[str, Any]:
        return {
            "function_calling": False,
            "streaming": self.enable_streaming,
            "tool_calling": False
        }


def run_cli():
    """
    Simple command-line interface to interact with a local LLM using the adapter.
    """
    parser = argparse.ArgumentParser(description="Run HuggingFace LLM in CLI")
    parser.add_argument("--model", type=str, default="mistral-7b", help="Model name or alias")
    parser.add_argument("--quant", action="store_true", help="Use quantized (4-bit) model")
    parser.add_argument("--stream", action="store_true", help="Enable streaming output")
    parser.add_argument("--token", type=str, default=None, help="Hugging Face Hub authentication token.")
    args = parser.parse_args()

    print(f"🤖 Using model: {args.model} (quantized={args.quant})")
    adapter = HuggingFaceAdapter(
        model_name=args.model,
        quantized=args.quant,
        stream=args.stream,
        auth_token=args.token
    )

    print("\nType 'exit' to quit.\n")
    
    history = []
    while True:
        try:
            user_input = input("You: ")
            if user_input.lower() in ["exit", "quit"]:
                break
            
            history.append(Message(role="user", content=user_input))
            
            response = adapter.invoke(history)
            
            if not args.stream:
                 print(f"Assistant: {response.content}\n")

            history.append(response)

        except KeyboardInterrupt:
            print("\n👋 Exiting...")
            break
        except Exception as e:
            print(f"\n❌ An unexpected error occurred: {e}", file=sys.stderr)

if __name__ == "__main__":
    run_cli()