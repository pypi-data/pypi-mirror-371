# fairlib.modules.memory/embedder.py
"""
This module provides concrete implementations of the AbstractEmbedder interface.

Embedders are responsible for converting text into numerical vectors, which is a
foundational step for semantic search and Retrieval-Augmented Generation (RAG).
This file includes a `DummyEmbedder` for testing and a functional
`SentenceTransformerEmbedder` for production use.
"""

import asyncio
from typing import List
from fairlib.core.interfaces.embedder import AbstractEmbedder

# --- Handle Optional Dependency ---
# This block safely imports the 'sentence_transformers' library. If the library
# is not installed, it sets a flag to False and the program can continue to run,
# allowing the use of other components like the DummyEmbedder.
try:
    from sentence_transformers import SentenceTransformer
    SENTENCE_TRANSFORMERS_AVAILABLE = True
except ImportError:
    SENTENCE_TRANSFORMERS_AVAILABLE = False
# ---

class DummyEmbedder(AbstractEmbedder):
    """
    A simple dummy embedder for testing and development purposes.

    This class allows the framework's RAG and memory components to operate
    without requiring a real, computationally expensive embedding model to be
    loaded. It returns fixed-size, predictable vectors of ones, which is useful
    for unit testing the data flow through the system.
    """
    def embed_documents(self, texts: list) -> List[List[float]]:
        """
        Generates a list of dummy vectors for a corresponding list of texts.
        The content of the texts is ignored.
        """
        # Create a list of dummy embeddings. Each embedding is a list of 10 floating-point 1s.
        return [[1.0] * 10 for _ in texts]

    def embed_query(self, text: str) -> List[float]:
        """
        Generates a dummy vector for a single text query. The content of the
        text is ignored.
        """
        # Return a single dummy embedding.
        return [1.0] * 10

    # Note: This class intentionally does not implement the 'aembed' methods.
    # It relies on the default asynchronous implementations provided by the
    # AbstractEmbedder base class, which is sufficient for this simple case.

class SentenceTransformerEmbedder(AbstractEmbedder):
    """
    A concrete implementation of AbstractEmbedder that uses the popular
    'sentence-transformers' library to create high-quality text embeddings.

    This class is a wrapper around a SentenceTransformer model, making it
    compatible with the FAIR-LLM framework's memory systems.
    """
    def __init__(self, model_name: str = 'all-MiniLM-L6-v2'):
        """
        Initializes the embedder and loads the specified sentence-transformer model.

        Args:
            model_name: The name of the model to use from the Hugging Face Hub.
                        The model will be downloaded automatically on first use.

        Raises:
            ImportError: If the 'sentence-transformers' library is not installed.
        """
        # Before attempting to use the library, check if it was successfully imported.
        if not SENTENCE_TRANSFORMERS_AVAILABLE:
            # Provide a helpful error message guiding the user on how to install the dependency.
            raise ImportError(
                "The 'sentence-transformers' library is not installed. "
                "Please install it to use SentenceTransformerEmbedder by running: pip install sentence-transformers"
            )

        # Load the specified model from the Hugging Face Hub. This can take time on first run.
        self.model = SentenceTransformer(model_name)
        print(f"✅ SentenceTransformerEmbedder initialized with model: {model_name}")

    def embed_documents(self, texts: List[str]) -> List[List[float]]:
        """
        Embeds a list of document strings into a list of numerical vectors.
        """
        # The 'encode' method returns a NumPy array, so we convert it to a standard Python list.
        return self.model.encode(texts).tolist()

    def embed_query(self, text: str) -> List[float]:
        """
        Embeds a single query string into a numerical vector.
        """
        # The 'encode' method returns a NumPy array, so we convert it to a standard Python list.
        return self.model.encode(text).tolist()

    # Note on async methods: The `aembed_documents` and `aembed_query` methods
    # are inherited from the AbstractEmbedder base class. The default implementation
    # correctly runs the synchronous `encode` method in a separate thread using
    # `asyncio.to_thread`, preventing it from blocking the main event loop.
    # This is sufficient for most use cases.
