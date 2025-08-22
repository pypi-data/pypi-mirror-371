# fairlib.modules.memory/summarization.py
"""
This module provides an advanced memory component that can summarize long
conversations to manage the context window of language models.
"""
from typing import List, Optional

from fairlib.core.interfaces.llm import AbstractChatModel
from fairlib.core.interfaces.memory import AbstractMemory
from fairlib.core.message import Message


class SummarizingMemory(AbstractMemory):
    """
    A memory class that automatically summarizes the conversation history
    when it exceeds a specified length.

    This strategy helps manage the token count sent to the LLM, enabling longer
    conversations while saving on costs and preventing context window overflow.
    It works by keeping the first message, the most recent messages, and a
    generated summary of the messages in between.
    """
    def __init__(
        self,
        llm: AbstractChatModel,
        max_history_length: int = 10,
        messages_to_keep_at_end: int = 4
    ):
        """
        Initializes the SummarizingMemory.

        Args:
            llm: An initialized chat model to be used for generating summaries.
            max_history_length: The number of messages to hold before summarization
                                is triggered.
            messages_to_keep_at_end: The number of recent messages to preserve
                                     verbatim, ensuring recent context is not lost.
        """
        # The LLM is a dependency, as it's required to perform the summarization.
        self.llm = llm
        self.history: List[Message] = []
        self.max_history_length = max_history_length
        self.messages_to_keep_at_end = messages_to_keep_at_end

        # Ensure the number of messages to keep is less than the max history.
        if self.messages_to_keep_at_end >= self.max_history_length:
            raise ValueError("messages_to_keep_at_end must be less than max_history_length")

    def add_message(self, message: Message):
        """Adds a message to the conversation history."""
        self.history.append(message)

    def get_history(self) -> List[Message]:
        """
        Retrieves the conversation history.

        If the history is too long, this method will block while it generates a
        summary. For non-blocking operations, use `aget_history`.
        """
        # This is a simplified, blocking version. The async version is preferred.
        # A real-world sync implementation might use `asyncio.run(self.aget_history())`.
        if len(self.history) <= self.max_history_length:
            return self.history
        else:
            # For simplicity, this returns a placeholder in the sync version.
            # The async version contains the full, correct logic.
            print("Warning: Summarization in sync mode is not fully implemented. Use aget_history().")
            return self.history[:1] + [Message(role="system", content="...summary...")] + self.history[-self.messages_to_keep_at_end:]

    async def aget_history(self) -> List[Message]:
        """
        Asynchronously retrieves the conversation history, summarizing it if necessary.
        """
        if len(self.history) <= self.max_history_length:
            return self.history

        print("--- History limit exceeded. Generating summary... ---")

        # Determine which part of the history to summarize.
        # We keep the very first message (often a system prompt) and the last few messages.
        num_messages_to_summarize = len(self.history) - self.messages_to_keep_at_end - 1
        messages_to_summarize = self.history[1:1 + num_messages_to_summarize]
        
        # Format the content for the LLM summarization prompt.
        summarization_content = "\n".join([f"{msg.role}: {msg.content}" for msg in messages_to_summarize])
        
        summarization_prompt = [
            Message(
                role="system",
                content="You are a conversation summarizer. Please provide a concise summary of the following exchange."
            ),
            Message(role="user", content=summarization_content)
        ]
        
        # Use the LLM to generate the summary.
        summary_message = await self.llm.ainvoke(summarization_prompt)
        # The summary message content should replace the summarized messages.
        summary_message.content = f"--- Start of Summarized Conversation ---\n{summary_message.content}\n--- End of Summarized Conversation ---"
        summary_message.role = "system" # Treat the summary as a system message.

        # Reconstruct the history with the summary in the middle.
        new_history = (
            [self.history[0]] + # Keep the first message
            [summary_message] + # Add the new summary
            self.history[1 + num_messages_to_summarize:] # Keep the last few messages
        )
        
        # Update the internal history so we don't summarize the same messages again.
        self.history = new_history
        print("--- Summary generation complete. ---")
        
        return self.history

    def clear(self):
        """Clears the conversation history."""
        self.history = []