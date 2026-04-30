"""End-to-end ingestion: pdf path -> Chunks (page images cached for the UI)."""
from __future__ import annotations

import hashlib
from dataclasses import dataclass
from pathlib import Path

import fitz

from pdfagent.config import CONFIG
from pdfagent.ingest.chunk import chunk_pdf
from pdfagent.ingest.extract import extract_pages
from pdfagent.ingest.tables import extract_tables
from pdfagent.ingest.ocr import ocr_page
from pdfagent.types import Chunk


@dataclass
class IngestResult:
    pdf_id: str
    pdf_path: str
    num_pages: int
    chunks: list[Chunk]
    page_text_by_page: dict[int, str]


def _hash_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for block in iter(lambda: f.read(1 << 16), b""):
            h.update(block)
    return h.hexdigest()[:16]


def _cache_page_images(pdf_path: Path, pdf_id: str, num_pages: int) -> None:
    out_dir = CONFIG.page_image_dir / pdf_id
    if out_dir.exists() and len(list(out_dir.glob("*.png"))) >= num_pages:
        return
    out_dir.mkdir(parents=True, exist_ok=True)
    doc = fitz.open(str(pdf_path))
    try:
        for i, page in enumerate(doc, start=1):
            target = out_dir / f"p{i:04d}.png"
            if target.exists():
                continue
            pix = page.get_pixmap(dpi=140)
            pix.save(str(target))
    finally:
        doc.close()


def ingest_pdf(pdf_path: str | Path) -> IngestResult:
    p = Path(pdf_path)
    if not p.exists():
        raise FileNotFoundError(p)
    pdf_id = _hash_file(p)

    pages, _headings = extract_pages(str(p))
    tables = extract_tables(str(p))

    ocr_text_by_page: dict[int, str] = {}
    for pc in pages:
        if pc.is_scanned:
            ocr_text_by_page[pc.page] = ocr_page(str(p), pc.page)

    chunks = chunk_pdf(pdf_id, pages, tables, ocr_text_by_page)

    page_text_by_page: dict[int, str] = {}
    for pc in pages:
        page_text_by_page[pc.page] = (
            pc.text if pc.text.strip() else ocr_text_by_page.get(pc.page, "")
        )

    _cache_page_images(p, pdf_id, len(pages))

    return IngestResult(
        pdf_id=pdf_id,
        pdf_path=str(p.resolve()),
        num_pages=len(pages),
        chunks=chunks,
        page_text_by_page=page_text_by_page,
    )
