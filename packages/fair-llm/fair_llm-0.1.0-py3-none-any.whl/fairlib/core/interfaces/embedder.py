import abc
import asyncio
from typing import List


class AbstractEmbedder(abc.ABC):
    """
    An abstract interface for text embedding models.

    The Embedder's role is to convert textual information into dense numerical
    vectors (embeddings). This is a foundational step for any semantic search
    or Retrieval-Augmented Generation (RAG) capability.

    This interface distinguishes between embedding a batch of documents (for
    ingestion into a vector store) and embedding a single query string (for
    performing a search).
    """

    @abc.abstractmethod
    def embed_documents(self, texts: List[str]) -> List[List[float]]:
        """Embeds a list of documents into a list of vectors."""
        ...

    async def aembed_documents(self, texts: List[str]) -> List[List[float]]:
        """Asynchronously embeds a list of documents."""
        # Provides a default async implementation by running the sync method in a thread.
        return await asyncio.to_thread(self.embed_documents, texts)

    @abc.abstractmethod
    def embed_query(self, text: str) -> List[float]:
        """Embeds a single query string into a vector."""
        ...

    async def aembed_query(self, text: str) -> List[float]:
        """Asynchronously embeds a single query."""
        # Provides a default async implementation.
        return await asyncio.to_thread(self.embed_query, text)