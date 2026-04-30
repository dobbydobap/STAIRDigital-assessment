"""Thin wrapper that fans out a (possibly decomposed) query into the store."""
from __future__ import annotations

from pdfagent.index.embeddings import get_embedder
from pdfagent.index.store import get_store
from pdfagent.types import Retrieved


def retrieve(
    pdf_id: str,
    queries: list[str],
    final_k: int = 5,
    first_stage_k: int = 30,
) -> list[Retrieved]:
    """Retrieve and merge top results across one or more sub-queries.

    De-duplicates by chunk_id, keeping the highest combined score.
    """
    if not queries:
        return []
    embedder = get_embedder()
    store = get_store()
    seen: dict[str, Retrieved] = {}
    for q in queries:
        if not q.strip():
            continue
        q_dense, q_sparse = embedder.encode_query(q)
        results = store.search(
            pdf_id=pdf_id,
            query_dense=q_dense,
            query_sparse=q_sparse,
            first_stage_k=first_stage_k,
            final_k=final_k,
        )
        for r in results:
            existing = seen.get(r.chunk.chunk_id)
            if existing is None or r.combined_score > existing.combined_score:
                seen[r.chunk.chunk_id] = r
    merged = sorted(seen.values(), key=lambda r: r.combined_score, reverse=True)
    return merged[:final_k]
