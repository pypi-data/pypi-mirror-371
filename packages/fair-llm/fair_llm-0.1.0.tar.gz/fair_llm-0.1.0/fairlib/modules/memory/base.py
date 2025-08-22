# memory/base.py

from typing import List
from abc import ABC, abstractmethod
from fairlib.core.message import Message
from fairlib.core.interfaces.memory import AbstractMemory, AbstractVectorStore
from typing import Union, Optional, List, Dict, Any


class WorkingMemory(AbstractMemory):
    """
    Manages the short-term, in-context memory for an agent's reasoning loop.
    This is essentially the conversation history.
    """
    def __init__(self, max_size: int = 20):
        self.history: List[Message] = []
        self.max_size = max_size

    def add_message(self, message: Message):
        """Adds a message to the history and trims if it exceeds max_size."""
        self.history.append(message)
        # Keep the history from growing indefinitely
        if len(self.history) > self.max_size:
            # Simple trimming strategy: remove the oldest messages after the system prompt
            self.history = self.history[:1] + self.history[-self.max_size+1:]

    def get_history(self) -> List[Message]:
        """Returns the current conversation history."""
        return self.history

    def clear(self):
        """Clears the memory."""
        self.history = []

class LongTermMemory(AbstractMemory):
    """
    Manages the long-term, retrievable memory for an agent using a vector store.
    Used for Retrieval-Augmented Generation (RAG).
    """
    def __init__(self, vector_store: AbstractVectorStore):
        self.vector_store = vector_store

    def add_document(self, content: Union[str, List[str]], metadata: Optional[Dict[str, Any]] = None):
        """Adds a document to the long-term memory (vector store)."""
        # This assumes the vector store handles embedding and indexing.
        if isinstance(content, str):
            content = [content]
        self.vector_store.add_documents(content, [metadata or {} for _ in content])

    def retrieve_relevant_chunks(self, query: str, top_k: int = 5) -> List[str]:
        """Retrieves the most relevant document chunks for a given query."""
        return self.vector_store.similarity_search(query, k=top_k)

    # These methods are part of the AbstractMemory interface but are less relevant
    # for a pure RAG store. They could be implemented to log queries, for example.
    def add_message(self, message: Message):
        pass

    def get_history(self) -> List[Message]:
        return []

    def clear(self):
        # Clearing a long-term memory is a destructive action, handle with care.
        print("Warning: Clearing long-term memory is not implemented by default.")
        pass
