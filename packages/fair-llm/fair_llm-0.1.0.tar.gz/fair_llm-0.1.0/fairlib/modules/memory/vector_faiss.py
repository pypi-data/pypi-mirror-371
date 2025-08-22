# fairlib/modules/memory/vector_faiss.py

from __future__ import annotations
import os
import pickle
from typing import List, Dict, Any, Optional
import numpy as np

from fairlib.core.interfaces.memory import AbstractVectorStore, AbstractEmbedder
from fairlib.core.types import Document

try:
    import faiss
    try:
        faiss.omp_set_num_threads(os.cpu_count() or 1)
    except Exception:
        pass
    _FAISS_AVAILABLE = True
except ImportError: 
    _FAISS_AVAILABLE = False

try:
    import torch
    _TORCH_AVAILABLE = True
except Exception: 
    _TORCH_AVAILABLE = False


class FaissVectorStore(AbstractVectorStore):
    """
    FAISS-backed vector store that stores and returns Document objects.
    """

    def __init__(
        self,
        embedder: AbstractEmbedder,
        index_dir: str = "out/vector_store",
        use_gpu: bool = False,
        normalize: bool = True,
        batch_size: Optional[int] = None,
    ):
        if not _FAISS_AVAILABLE:
            raise ImportError("faiss is not installed. Install faiss-cpu or faiss-gpu.")

        self.embedder = embedder
        self.index_dir = index_dir
        self.use_gpu = bool(use_gpu)
        self.normalize = bool(normalize)
        self.batch_size = batch_size

        self._index_path = os.path.join(self.index_dir, "index.faiss")
        self._mapping_path = os.path.join(self.index_dir, "mapping.pkl")

        self.index = None                 # faiss.Index (wrapped in IndexIDMap)
        self.gpu_index = None             # optional GPU mirror
        self.index_dim: Optional[int] = None
        self.faiss_on_gpu = False

        # Store Document objects in memory
        self._documents: List[Document] = []

    def add_documents(self, documents: List[Document]):
        if not documents:
            return

        embs = self._encode_documents(documents)  # (N, D) float32
        if self.normalize:
            faiss.normalize_L2(embs)

        self._ensure_index(embs.shape[1])
        start_id = len(self._documents)
        ids = np.arange(start_id, start_id + len(documents), dtype="int64")
        self.index.add_with_ids(embs, ids)

        self._documents.extend(documents)
        self._maybe_refresh_gpu()
        self.persist()

    def similarity_search(self, query: str, k: int = 5) -> List[Document]:
        if not query or self.index is None or self.ntotal == 0:
            return []

        q = self._encode_query(query)  # (1, D)
        if self.normalize:
            faiss.normalize_L2(q)

        search_index = self.gpu_index if (self.faiss_on_gpu and self.gpu_index is not None) else self.index
        _, I = search_index.search(q, min(k, self.ntotal))

        hits: List[Document] = []
        for idx in I[0]:
            if 0 <= idx < len(self._documents):
                hits.append(self._documents[idx])
        return hits

    async def asimilarity_search(self, query: str, k: int = 5) -> List[Document]:
        # Default async behavior is fine, but explicit override is ok too.
        import asyncio
        return await asyncio.to_thread(self.similarity_search, query, k)

    @property
    def ntotal(self) -> int:
        return int(self.index.ntotal) if self.index is not None else 0

    def load(self) -> bool:
        """Load index and mapping from disk. Returns True if successful."""
        if not (os.path.exists(self._index_path) and os.path.exists(self._mapping_path)):
            return False

        cpu_index = faiss.read_index(self._index_path)
        self.index = cpu_index
        self.index_dim = cpu_index.d

        with open(self._mapping_path, "rb") as f:
            data = pickle.load(f)

        texts: List[str] = list(data.get("page_contents", []))
        metas: List[Dict[str, Any]] = list(data.get("metadatas", [{} for _ in texts]))
        self._documents = [Document(t, m) for t, m in zip(texts, metas)]

        if self.index_dim is None:
            self.index_dim = data.get("dim")

        self._maybe_move_to_gpu()
        return True

    def persist(self):
        """Persist CPU index and mappings to disk."""
        if self.index is None:
            return
        os.makedirs(self.index_dir, exist_ok=True)
        faiss.write_index(self.index, self._index_path)

        texts = [d.page_content for d in self._documents]
        metas = [d.metadata for d in self._documents]
        with open(self._mapping_path, "wb") as f:
            pickle.dump({"page_contents": texts, "metadatas": metas, "dim": self.index_dim}, f)

    def clear(self):
        """Clear in-memory index/mappings (does not delete files)."""
        self.index = None
        self.gpu_index = None
        self.index_dim = None
        self.faiss_on_gpu = False
        self._documents = []

    def _ensure_index(self, dim: int):
        if self.index is None:
            base = faiss.IndexFlatIP(dim)
            self.index = faiss.IndexIDMap(base)
            self.index_dim = dim
            self._maybe_move_to_gpu()
        else:
            if self.index_dim is not None and self.index_dim != dim:
                raise ValueError(f"Embedding dimension mismatch: existing={self.index_dim}, new={dim}")

    def _maybe_move_to_gpu(self):
        """Create/refresh a GPU mirror if requested and available."""
        if not self.use_gpu:
            self.faiss_on_gpu = False
            self.gpu_index = None
            return
        if not _TORCH_AVAILABLE or not torch.cuda.is_available():
            self.faiss_on_gpu = False
            self.gpu_index = None
            return
        try: 
            res = faiss.StandardGpuResources()
            self.gpu_index = faiss.index_cpu_to_gpu(res, 0, self.index)
            self.faiss_on_gpu = True
        except Exception:
            self.faiss_on_gpu = False
            self.gpu_index = None

    def _maybe_refresh_gpu(self):
        """Re-create GPU mirror from CPU after updates."""
        if self.faiss_on_gpu and self.index is not None:
            self._maybe_move_to_gpu()

    def _encode_documents(self, documents: List[Document]) -> np.ndarray:
        """Encode Document.page_content to float32 ndarray."""
        texts = [d.page_content for d in documents]
        embs = self.embedder.embed_documents(texts)
        return np.asarray(embs, dtype="float32")

    def _encode_query(self, query: str) -> np.ndarray:
        emb = self.embedder.embed_query(query)
        arr = np.asarray(emb, dtype="float32")
        return arr[None, :] if arr.ndim == 1 else arr.astype("float32", copy=False)
