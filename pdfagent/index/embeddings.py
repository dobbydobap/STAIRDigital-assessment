"""bge-m3 embedder. Returns dense + sparse weights in one pass.

bge-m3 supports 100+ languages, gives a dense vector (1024-d) and a
lexical sparse weighting per token. We combine the two at retrieval time
for a hybrid score that needs no extra reranker.
"""
from __future__ import annotations

from functools import lru_cache
from typing import Iterable

import numpy as np


class Embedder:
    """Lazy bge-m3 wrapper. Heavy import is deferred until first use."""

    def __init__(self, model_name: str = "BAAI/bge-m3", use_fp16: bool = True) -> None:
        self.model_name = model_name
        self.use_fp16 = use_fp16
        self._model = None
        self._dim = 1024

    @property
    def model(self):
        if self._model is None:
            from FlagEmbedding import BGEM3FlagModel
            self._model = BGEM3FlagModel(self.model_name, use_fp16=self.use_fp16)
        return self._model

    @property
    def dim(self) -> int:
        return self._dim

    def encode_documents(self, texts: list[str]) -> tuple[np.ndarray, list[dict[str, float]]]:
        out = self.model.encode(
            texts,
            return_dense=True,
            return_sparse=True,
            return_colbert_vecs=False,
        )
        dense = np.asarray(out["dense_vecs"], dtype=np.float32)
        sparse = [
            {str(k): float(v) for k, v in d.items()}
            for d in out["lexical_weights"]
        ]
        return dense, sparse

    def encode_query(self, text: str) -> tuple[np.ndarray, dict[str, float]]:
        out = self.model.encode(
            [text],
            return_dense=True,
            return_sparse=True,
            return_colbert_vecs=False,
        )
        dense = np.asarray(out["dense_vecs"][0], dtype=np.float32)
        sparse = {str(k): float(v) for k, v in out["lexical_weights"][0].items()}
        return dense, sparse

    @staticmethod
    def sparse_score(q: dict[str, float], d: dict[str, float]) -> float:
        if not q or not d:
            return 0.0
        if len(q) > len(d):
            q, d = d, q
        s = 0.0
        for k, v in q.items():
            w = d.get(k)
            if w is not None:
                s += v * w
        return float(s)


@lru_cache(maxsize=1)
def get_embedder() -> Embedder:
    return Embedder()


def chunked(iterable: Iterable, size: int):
    buf: list = []
    for x in iterable:
        buf.append(x)
        if len(buf) == size:
            yield buf
            buf = []
    if buf:
        yield buf
