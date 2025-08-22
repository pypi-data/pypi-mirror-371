# memory/vector_store.py

from typing import List, Dict, Any, Optional
from fairlib.core.interfaces.memory import AbstractVectorStore, AbstractEmbedder

from fairlib.modules.memory.vector_faiss import FaissVectorStore  # re-export, users can import faiss store from this file

"""
==========================================
Module: vector_store.py
==========================================

This module provides concrete implementations of the `AbstractVectorStore` interface,
which defines a common interface for storing and querying document embeddings
in Retrieval-Augmented Generation (RAG) systems.

RAG systems depend on vector stores to store high-dimensional vector representations
(aka "embeddings") of text and retrieve the most semantically similar content
to a given query.

Two implementations are provided in this module:
1. InMemoryVectorStore – a lightweight, non-persistent store for quick prototyping.
2. ChromaDBVectorStore – a production-ready vector store using ChromaDB as backend.

Both classes adhere to the `AbstractVectorStore` contract.
"""

# ----------------------------------------------------------------------
# InMemoryVectorStore: Minimal demo implementation for debugging or learning
# ----------------------------------------------------------------------

class InMemoryVectorStore(AbstractVectorStore):
    """
    A simple in-memory vector store. This class is useful for testing,
    demos, or understanding how vector stores work without using an external DB.

    Limitations:
        - No real vector math (no embedding comparisons or distance calculations)
        - No persistence (data is lost when process exits)
    """
    def __init__(self):
        # `vectors` stores empty placeholders for now, indexed by hashed document IDs.
        self.vectors: Dict[str, List[float]] = {}

        # `documents` stores the actual document strings, keyed by the same ID.
        self.documents: Dict[str, str] = {}

    def add_documents(self, documents: List[str], metadatas: Optional[List[Dict[str, Any]]] = None):
        """
        Stores documents in memory using a hash of the text as a unique ID.
        Note: Embedding generation is skipped here for simplicity.

        Args:
            documents: A list of text chunks to store.
            metadatas: Unused in this version, but kept for interface compatibility.
        """
        for doc in documents:
            doc_id = str(hash(doc))  # Use the hash of the text as a simple unique ID.
            self.documents[doc_id] = doc
            self.vectors[doc_id] = []  # Placeholder for a real vector (not used in demo)
        
        print(f"Added {len(documents)} documents to in-memory store.")

    def similarity_search(self, query: str, k: int = 5) -> List[str]:
        """
        Returns the first `k` documents from memory. No similarity is computed.

        Args:
            query: Ignored in this implementation.
            k: Number of documents to return.

        Returns:
            A list of up to `k` documents.
        """
        return list(self.documents.values())[:k]


# ----------------------------------------------------------------------
# ChromaDBVectorStore: Production-grade implementation using ChromaDB
# ----------------------------------------------------------------------

class ChromaDBVectorStore(AbstractVectorStore):
    """
    A full-featured vector store implementation backed by ChromaDB.

    ChromaDB is a high-performance, open-source vector database that supports
    similarity search, filtering, and more. This implementation uses ChromaDB's
    native Python client.

    Typical usage in a RAG pipeline:
        - Embed incoming documents
        - Add them to ChromaDB
        - At query time, embed the query
        - Run similarity search against stored vectors
    """

    def __init__(self, embedder: AbstractEmbedder, client: Any, collection_name: str = "fair_llm_collection"):
        """
        Constructor for ChromaDBVectorStore.

        Args:
            embedder: An object that provides `embed_documents()` and `embed_query()` methods.
                      Must implement AbstractEmbedder.
            client: A ChromaDB client object (typically from `chromadb.Client()`).
            collection_name: Name of the ChromaDB collection to use or create.
        """
        try:
            import chromadb  # Just to confirm the library is installed
        except ImportError:
            raise ImportError("ChromaDB is not installed. Run `pip install chromadb` to use this backend.")

        self.embedder = embedder
        self.client = client
        self.collection = self.client.get_or_create_collection(name=collection_name)

    def add_documents(self, documents: List[str], metadatas: Optional[List[Dict[str, Any]]] = None):
        """
        Embeds documents using the provided embedder, and adds them to the ChromaDB collection.

        Args:
            documents: A list of raw document strings to embed and store.
            metadatas: Optional metadata dictionaries. Each dict should contain at least one key-value pair.

        Raises:
            ValueError: If metadata is provided but is empty (ChromaDB requires non-empty metadata).
        """
        if not documents:
            return  # Nothing to do

        # Convert documents to vectors
        embeddings = self.embedder.embed_documents(documents)

        # Generate unique IDs for each document (based on hash of content)
        ids = [str(hash(doc)) for doc in documents]

        # Ensure metadatas is a non-empty dict per document (required by ChromaDB)
        # TODO: We need to make this more robust by accepting or discovering 
        #       additional metadata that can be included for each chunck! 
        metadatas = metadatas if metadatas else [{"source": f"chunk_{i}"} for i in range(len(documents))]

        # Add to ChromaDB collection
        self.collection.add(
            embeddings=embeddings,
            documents=documents,
            metadatas=metadatas,
            ids=ids
        )

    def similarity_search(self, query: str, k: int = 5) -> List[str]:
        """
        Performs semantic similarity search against the ChromaDB collection.

        Args:
            query: A natural language string.
            k: The number of top documents to retrieve based on similarity.

        Returns:
            A list of up to `k` documents, sorted by similarity to the query.
        """
        if not query:
            return []

        # Generate embedding for the query
        query_embedding = self.embedder.embed_query(query)

        # Query the ChromaDB vector index
        results = self.collection.query(
            query_embeddings=[query_embedding],
            n_results=k
        )

        # Return documents if found, else an empty list
        return results['documents'][0] if results and results['documents'] else []