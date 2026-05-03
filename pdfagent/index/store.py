"""ChromaDB-backed vector store, persisted by PDF hash.

We store dense vectors in Chroma (it serves first-stage cosine retrieval) and
keep the sparse weights as a JSON blob in metadata for re-scoring at query time.
"""
from __future__ import annotations

import json
from functools import lru_cache
from typing import Iterable

import chromadb
from chromadb.config import Settings

from pdfagent.config import CONFIG
from pdfagent.index.embeddings import Embedder, chunked, get_embedder
from pdfagent.types import Chunk, Retrieved

_COLLECTION = "pdf_chunks"
_BATCH = 32

_ALPHA_DENSE = 0.6  # weight on dense; sparse gets (1 - alpha)


class VectorStore:
    def __init__(self, persist_dir: str | None = None) -> None:
        self.persist_dir = persist_dir or str(CONFIG.chroma_dir)
        self._client = chromadb.PersistentClient(
            path=self.persist_dir,
            settings=Settings(anonymized_telemetry=False, allow_reset=False),
        )
        self._collection = self._client.get_or_create_collection(
            name=_COLLECTION,
            metadata={"hnsw:space": "cosine"},
        )

    def has_pdf(self, pdf_id: str) -> bool:
        try:
            res = self._collection.get(where={"pdf_id": pdf_id}, limit=1)
            return bool(res.get("ids"))
        except Exception:
            return False

    def list_pdfs(self) -> list[str]:
        try:
            res = self._collection.get(include=["metadatas"])
        except Exception:
            return []
        seen: set[str] = set()
        for md in res.get("metadatas") or []:
            if md and md.get("pdf_id"):
                seen.add(md["pdf_id"])
        return sorted(seen)

    def delete_pdf(self, pdf_id: str) -> None:
        self._collection.delete(where={"pdf_id": pdf_id})

    def upsert_chunks(self, chunks: list[Chunk], embedder: Embedder | None = None) -> int:
        if not chunks:
            return 0
        emb = embedder or get_embedder()
        added = 0
        try:
            from tqdm import tqdm
            iterator = tqdm(
                list(chunked(chunks, _BATCH)),
                desc=f"embedding {len(chunks)} chunks",
                unit="batch",
            )
        except ImportError:
            iterator = chunked(chunks, _BATCH)
        for batch in iterator:
            texts = [c.text for c in batch]
            dense, sparse = emb.encode_documents(texts)
            ids = [c.chunk_id for c in batch]
            metadatas = [
                {
                    "pdf_id": c.pdf_id,
                    "page": int(c.page),
                    "section_path": c.section_path or "",
                    "chunk_type": c.chunk_type,
                    "char_start": int(c.char_start),
                    "char_end": int(c.char_end),
                    "sparse": json.dumps(sparse[i]),
                }
                for i, c in enumerate(batch)
            ]
            self._collection.upsert(
                ids=ids,
                documents=texts,
                metadatas=metadatas,
                embeddings=dense.tolist(),
            )
            added += len(batch)
        return added

    def search(
        self,
        pdf_id: str,
        query_dense,
        query_sparse: dict[str, float],
        first_stage_k: int = 30,
        final_k: int = 5,
        alpha: float = _ALPHA_DENSE,
    ) -> list[Retrieved]:
        first_stage_k = max(first_stage_k, final_k)
        res = self._collection.query(
            query_embeddings=[query_dense.tolist()],
            n_results=first_stage_k,
            where={"pdf_id": pdf_id},
            include=["metadatas", "documents", "distances"],
        )
        ids = (res.get("ids") or [[]])[0]
        if not ids:
            return []
        docs = (res.get("documents") or [[]])[0]
        metas = (res.get("metadatas") or [[]])[0]
        dists = (res.get("distances") or [[]])[0]

        # Chroma returns cosine distance (smaller = more similar). Convert to similarity.
        candidates: list[Retrieved] = []
        from pdfagent.types import Chunk
        for i, cid in enumerate(ids):
            md = metas[i] or {}
            text = docs[i] or ""
            dense_sim = max(0.0, 1.0 - float(dists[i]))
            try:
                doc_sparse = json.loads(md.get("sparse") or "{}")
            except Exception:
                doc_sparse = {}
            sparse_sim = Embedder.sparse_score(query_sparse, doc_sparse)
            chunk = Chunk(
                chunk_id=cid,
                pdf_id=md.get("pdf_id", pdf_id),
                page=int(md.get("page", 0)),
                section_path=md.get("section_path", ""),
                chunk_type=md.get("chunk_type", "text"),
                text=text,
                char_start=int(md.get("char_start", 0)),
                char_end=int(md.get("char_end", 0)),
            )
            candidates.append(Retrieved(
                chunk=chunk,
                dense_score=dense_sim,
                sparse_score=sparse_sim,
                combined_score=0.0,
            ))

        if candidates:
            max_dense = max(c.dense_score for c in candidates) or 1.0
            max_sparse = max(c.sparse_score for c in candidates) or 1.0
            for c in candidates:
                d = c.dense_score / max_dense
                s = c.sparse_score / max_sparse if max_sparse else 0.0
                c.combined_score = alpha * d + (1.0 - alpha) * s

        candidates.sort(key=lambda r: r.combined_score, reverse=True)
        return candidates[:final_k]


@lru_cache(maxsize=1)
def get_store() -> VectorStore:
    return VectorStore()
