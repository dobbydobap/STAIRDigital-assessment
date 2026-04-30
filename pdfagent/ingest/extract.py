"""PyMuPDF text extraction with heading detection.

Per page we yield: full_text, heading list, blocks. Heading detection uses
the PDF's table-of-contents when available, otherwise font-size heuristics
on text spans.
"""
from __future__ import annotations

import statistics
from dataclasses import dataclass

import fitz  # PyMuPDF


@dataclass
class Heading:
    level: int
    title: str
    page: int


@dataclass
class PageContent:
    page: int
    text: str
    headings: list[Heading]
    is_scanned: bool


def _toc_headings(doc: "fitz.Document") -> list[Heading]:
    out: list[Heading] = []
    for entry in doc.get_toc(simple=True) or []:
        level, title, page = entry[0], entry[1], entry[2]
        out.append(Heading(level=int(level), title=str(title).strip(), page=int(page)))
    return out


def _heuristic_headings(page: "fitz.Page") -> list[Heading]:
    """Spans whose font size is materially larger than the page median are headings."""
    blocks = page.get_text("dict").get("blocks", [])
    sizes: list[float] = []
    candidates: list[tuple[float, str]] = []
    for b in blocks:
        for line in b.get("lines", []):
            spans = line.get("spans", [])
            if not spans:
                continue
            line_text = "".join(s.get("text", "") for s in spans).strip()
            if not line_text:
                continue
            max_size = max(float(s.get("size", 0)) for s in spans)
            sizes.append(max_size)
            candidates.append((max_size, line_text))
    if not sizes:
        return []
    median = statistics.median(sizes)
    threshold = median * 1.20
    headings = []
    for size, text in candidates:
        if size >= threshold and 3 <= len(text) <= 200 and not text.endswith("."):
            level = 1 if size >= median * 1.6 else 2 if size >= median * 1.35 else 3
            headings.append(Heading(level=level, title=text, page=page.number + 1))
    return headings


def _page_is_scanned(page: "fitz.Page") -> bool:
    text = page.get_text("text") or ""
    return len(text.strip()) < 50


def extract_pages(pdf_path: str) -> tuple[list[PageContent], list[Heading]]:
    """Returns per-page content and the merged heading list.

    Falls back to per-page heuristics for headings when no TOC is present.
    Pages flagged as scanned are returned with empty text — the OCR layer
    handles them.
    """
    doc = fitz.open(pdf_path)
    toc = _toc_headings(doc)
    use_toc = len(toc) > 0

    pages: list[PageContent] = []
    headings: list[Heading] = list(toc)

    for i, page in enumerate(doc, start=1):
        scanned = _page_is_scanned(page)
        text = "" if scanned else (page.get_text("text") or "")
        page_headings: list[Heading]
        if use_toc:
            page_headings = [h for h in toc if h.page == i]
        else:
            page_headings = _heuristic_headings(page)
            headings.extend(page_headings)
        pages.append(
            PageContent(
                page=i,
                text=text,
                headings=page_headings,
                is_scanned=scanned,
            )
        )

    doc.close()
    return pages, headings
