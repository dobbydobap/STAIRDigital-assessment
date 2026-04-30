"""High-level service: ingest_and_index, chat. The single API/UI/eval entry point."""
from __future__ import annotations

import shutil
from pathlib import Path

from pdfagent.config import CONFIG
from pdfagent.index.store import get_store
from pdfagent.ingest.pipeline import ingest_pdf
from pdfagent.orchestrator import TurnResult, chat_turn
from pdfagent.registry import PdfRecord, get_registry


def ingest_and_index(pdf_path: str | Path, original_filename: str | None = None) -> PdfRecord:
    """Ingest, embed, persist, and register a PDF. Idempotent by file hash."""
    src = Path(pdf_path)
    if not src.exists():
        raise FileNotFoundError(src)

    # Move/copy into the uploads dir so we own the file lifecycle.
    result = ingest_pdf(src)
    stored_path = CONFIG.uploads_dir / f"{result.pdf_id}.pdf"
    if not stored_path.exists():
        shutil.copy2(src, stored_path)

    store = get_store()
    if not store.has_pdf(result.pdf_id):
        store.upsert_chunks(result.chunks)

    languages: list[str] = []
    has_tables = any(c.chunk_type == "table" for c in result.chunks)
    has_ocr = any(c.chunk_type == "ocr" for c in result.chunks)

    rec = PdfRecord(
        pdf_id=result.pdf_id,
        original_filename=original_filename or src.name,
        pdf_path=str(stored_path.resolve()),
        num_pages=result.num_pages,
        page_text_by_page=result.page_text_by_page,
        has_tables=has_tables,
        has_ocr=has_ocr,
        languages_detected=languages,
    )
    get_registry().upsert(rec)
    return rec


def chat(
    pdf_id: str,
    query: str,
    history: list[dict[str, str]] | None = None,
    final_k: int = 5,
) -> TurnResult:
    rec = get_registry().get(pdf_id)
    if rec is None:
        raise KeyError(f"unknown pdf_id: {pdf_id}")
    return chat_turn(
        pdf_id=pdf_id,
        query=query,
        page_text_by_page=rec.page_text_by_page,
        history=history or [],
        final_k=final_k,
    )
