# fairlib/modules/memory/retriever_rerank.py

from __future__ import annotations
import asyncio
from typing import List
from fairlib.core.interfaces.memory import AbstractRetriever
from fairlib.core.types import Document


class CrossEncoderRerankingRetriever(AbstractRetriever):
    """
    Wraps another retriever and re-ranks its candidates with a CrossEncoder.
    """
    def __init__(self, base: AbstractRetriever, cross_encoder, rerank_k: int = 20):
        self.base = base
        self.cross_encoder = cross_encoder
        self.rerank_k = int(rerank_k)

    def retrieve(self, query: str, top_k: int = 5, **kwargs) -> List[Document]:
        candidates: List[Document] = self.base.retrieve(query, top_k=self.rerank_k, **kwargs) or []
        if not candidates:
            return []

        pairs = [(query, doc.page_content) for doc in candidates]
        scores = self.cross_encoder.predict(pairs)  # returns iterable of floats

        order = sorted(range(len(candidates)), key=lambda i: float(scores[i]), reverse=True)
        return [candidates[i] for i in order[:top_k]]

    async def aretrieve(self, query: str, top_k: int = 5, **kwargs) -> List[Document]:
        candidates: List[Document] = await self.base.aretrieve(query, top_k=self.rerank_k, **kwargs)
        if not candidates:
            return []

        pairs = [(query, doc.page_content) for doc in candidates]
        scores = await asyncio.to_thread(self.cross_encoder.predict, pairs)

        order = sorted(range(len(candidates)), key=lambda i: float(scores[i]), reverse=True)
        return [candidates[i] for i in order[:top_k]]
