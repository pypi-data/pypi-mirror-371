# fairlib.core.interfaces/memory.py
"""
This module defines the abstract interfaces for all memory-related components
in the framework. These contracts ensure that different memory systems and their
sub-components are interchangeable and support both sync and async operations.
"""

import abc
import asyncio
from typing import List, Dict, Any, Optional
from ..message import Message
from ..types import Document


class AbstractMemory(abc.ABC):
    """
    A high-level interface for an agent's conversational memory.
    """
    @abc.abstractmethod
    def add_message(self, message: Message):
        """Adds a message to the memory."""
        ...

    async def aadd_message(self, message: Message):
        """Asynchronously adds a message to the memory."""
        return self.add_message(message)

    @abc.abstractmethod
    def get_history(self) -> List[Message]:
        """Retrieves the full conversational history."""
        ...

    async def aget_history(self) -> List[Message]:
        """Asynchronously retrieves the full conversational history."""
        return self.get_history()

    @abc.abstractmethod
    def clear(self):
        """Clears the memory of all messages."""
        ...


class AbstractEmbedder(abc.ABC):
    """
    An interface for a class that can convert text into numerical vectors.
    """
    @abc.abstractmethod
    def embed_documents(self, texts: List[str]) -> List[List[float]]:
        """Synchronously embeds a list of documents."""
        ...

    async def aembed_documents(self, texts: List[str]) -> List[List[float]]:
        """Asynchronously embeds a list of documents."""
        return await asyncio.to_thread(self.embed_documents, texts)

    @abc.abstractmethod
    def embed_query(self, text: str) -> List[float]:
        """Synchronously embeds a single query text."""
        ...

    async def aembed_query(self, text: str) -> List[float]:
        """Asynchronously embeds a single query text."""
        return await asyncio.to_thread(self.embed_query, text)


class AbstractVectorStore(abc.ABC):
    """
    An interface for a vector database that stores documents and their
    embeddings for efficient similarity searching.
    """
    @abc.abstractmethod
    def add_documents(self, documents: List[Document]):
        """
        Adds documents to the vector store. The implementation should handle
        embedding the documents before storage.
        """
        ...

    @abc.abstractmethod
    def similarity_search(self, query: str, k: int = 5) -> List[Document]:
        """
        Synchronously finds the `k` most similar document chunks to a given
        query string. The implementation should handle embedding the query.
        """
        ...

    async def asimilarity_search(self, query: str, k: int = 5) -> List[Document]:
        """
        Asynchronously finds the `k` most similar document chunks to a query.
        """
        # Provides a default async implementation.
        return await asyncio.to_thread(self.similarity_search, query, k=k)


class AbstractRetriever(abc.ABC):
    """
    An interface for retrieving relevant documents from a vector store.
    This acts as a bridge between the agent's tools and the vector store.
    """
    @abc.abstractmethod
    def retrieve(self, query: str, top_k: int = 5, **kwargs) -> List[Document]:
        """Synchronously retrieves the top_k relevant documents for a query."""
        ...

    @abc.abstractmethod
    async def aretrieve(self, query: str, top_k: int = 5, **kwargs) -> List[Document]:
        """Asynchronously retrieves the top_k relevant documents for a query."""
        ...