"""Section-aware chunking.

Headings split text into sections; each section is then split into ~500-token
chunks with ~80-token overlap (token ≈ 4 chars heuristic to avoid a tokenizer
dependency at chunk time — bge-m3 will re-tokenize at embed time anyway).
"""
from __future__ import annotations

import hashlib
import re

from pdfagent.ingest.extract import Heading, PageContent
from pdfagent.ingest.tables import TableChunk
from pdfagent.types import Chunk

CHARS_PER_TOKEN = 4
TARGET_TOKENS = 500
OVERLAP_TOKENS = 80


def _chunk_id(pdf_id: str, page: int, idx: int, chunk_type: str) -> str:
    h = hashlib.sha1(f"{pdf_id}:{page}:{idx}:{chunk_type}".encode()).hexdigest()[:12]
    return f"{pdf_id[:8]}-{page:04d}-{chunk_type[:1]}-{h}"


def _split_text(text: str, target_chars: int, overlap_chars: int) -> list[tuple[int, int, str]]:
    """Greedy splitter that prefers paragraph then sentence boundaries."""
    if len(text) <= target_chars:
        return [(0, len(text), text)]

    out: list[tuple[int, int, str]] = []
    start = 0
    n = len(text)
    while start < n:
        end = min(start + target_chars, n)
        if end < n:
            # try paragraph break, then sentence, then whitespace
            for sep in ("\n\n", "\n", ". ", " "):
                idx = text.rfind(sep, start + int(target_chars * 0.5), end)
                if idx != -1:
                    end = idx + len(sep)
                    break
        chunk_text = text[start:end].strip()
        if chunk_text:
            out.append((start, end, chunk_text))
        if end >= n:
            break
        start = max(end - overlap_chars, start + 1)
    return out


def _section_path_for(page: int, char_offset: int, headings_by_page: dict[int, list[Heading]]) -> str:
    """Heuristic: nearest heading at or before this page, joined into a path."""
    path: list[str] = []
    for p in sorted(headings_by_page):
        if p > page:
            break
        for h in headings_by_page[p]:
            while len(path) >= h.level:
                path.pop()
            path.append(h.title)
    return " > ".join(path) if path else ""


def chunk_pdf(
    pdf_id: str,
    pages: list[PageContent],
    tables: list[TableChunk],
    ocr_text_by_page: dict[int, str],
) -> list[Chunk]:
    headings_by_page: dict[int, list[Heading]] = {}
    for p in pages:
        if p.headings:
            headings_by_page[p.page] = p.headings

    chunks: list[Chunk] = []
    target_chars = TARGET_TOKENS * CHARS_PER_TOKEN
    overlap_chars = OVERLAP_TOKENS * CHARS_PER_TOKEN

    for p in pages:
        body = p.text
        chunk_type = "text"
        if p.is_scanned:
            body = ocr_text_by_page.get(p.page, "")
            chunk_type = "ocr"
        if not body or not body.strip():
            continue
        body = re.sub(r"[ \t]+\n", "\n", body)
        body = re.sub(r"\n{3,}", "\n\n", body)
        for idx, (a, b, t) in enumerate(_split_text(body, target_chars, overlap_chars)):
            chunks.append(
                Chunk(
                    chunk_id=_chunk_id(pdf_id, p.page, idx, chunk_type),
                    pdf_id=pdf_id,
                    page=p.page,
                    section_path=_section_path_for(p.page, a, headings_by_page),
                    chunk_type=chunk_type,
                    text=t,
                    char_start=a,
                    char_end=b,
                )
            )

    for idx, tbl in enumerate(tables):
        chunks.append(
            Chunk(
                chunk_id=_chunk_id(pdf_id, tbl.page, idx, "table"),
                pdf_id=pdf_id,
                page=tbl.page,
                section_path=_section_path_for(tbl.page, 0, headings_by_page),
                chunk_type="table",
                text=tbl.markdown,
            )
        )

    return chunks
