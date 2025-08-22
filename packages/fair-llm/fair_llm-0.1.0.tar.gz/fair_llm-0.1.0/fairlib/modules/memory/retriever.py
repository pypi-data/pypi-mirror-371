# fairlib.modules.memory/retriever.py
"""
This module provides a concrete implementation of the AbstractRetriever interface.
Retrievers are responsible for fetching relevant information from a vector store.
"""
from typing import List, Any
from fairlib.core.interfaces.memory import AbstractRetriever, AbstractVectorStore
from fairlib.core.types import Document


class SimpleRetriever(AbstractRetriever):
    """
    A straightforward implementation of the AbstractRetriever interface.

    This class acts as a thin wrapper around a vector store. Its primary role
    is to expose the vector store's search functionality to the rest of the
    framework (e.g., to a `RetrieverTool` used by an agent) in a standardized way.
    It aligns with the design that the Vector Store itself handles the embedding
    of queries.
    """
    def __init__(self, vector_store: AbstractVectorStore):
        """
        Initializes the SimpleRetriever.

        Args:
            vector_store: An initialized, concrete instance of AbstractVectorStore
                          that this retriever will query against.
        """
        # The retriever's sole dependency is the vector store it will search.
        self.vector_store = vector_store
        print("✅ SimpleRetriever initialized.")

    def retrieve(self, query: str, top_k: int = 5, **kwargs: Any) -> List[Document]:
        """
        Synchronously retrieves the top_k relevant documents for a query.

        This method implements the abstract method from AbstractRetriever and
        delegates the search operation directly to the vector store.

        Args:
            query: The raw text query from the user.
            top_k: The number of documents to retrieve.
            **kwargs: Placeholder for any additional search parameters.

        Returns:
            A list of Document objects, each containing the content and metadata
            of a relevant document chunk.
        """
        # The vector store handles the embedding of the query and the search.
        return self.vector_store.similarity_search(query, k=top_k)

    async def aretrieve(self, query: str, top_k: int = 5, **kwargs: Any) -> List[Document]:
        """
        Asynchronously retrieves the top_k relevant documents for a query.

        This method implements the abstract method from AbstractRetriever and
        delegates the async search operation to the vector store.

        Args:
            query: The raw text query from the user.
            top_k: The number of documents to retrieve.
            **kwargs: Placeholder for any additional search parameters.

        Returns:
            A list of Document objects.
        """
        # Await the asynchronous search method of the vector store.
        return await self.vector_store.asimilarity_search(query, k=top_k)