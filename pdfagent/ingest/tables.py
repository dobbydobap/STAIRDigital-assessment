"""Table extraction via PyMuPDF, serialized as Markdown so it embeds well."""
from __future__ import annotations

from dataclasses import dataclass

import fitz


@dataclass
class TableChunk:
    page: int
    markdown: str


def _row_to_md(row: list[str | None]) -> str:
    cells = [(c or "").replace("|", "\\|").replace("\n", " ").strip() for c in row]
    return "| " + " | ".join(cells) + " |"


def _table_to_md(rows: list[list[str | None]]) -> str:
    if not rows:
        return ""
    header = rows[0]
    body = rows[1:] if len(rows) > 1 else []
    lines = [_row_to_md(header), "| " + " | ".join(["---"] * len(header)) + " |"]
    lines.extend(_row_to_md(r) for r in body)
    return "\n".join(lines)


def extract_tables(pdf_path: str) -> list[TableChunk]:
    """Return one TableChunk per table found, with page metadata."""
    doc = fitz.open(pdf_path)
    out: list[TableChunk] = []
    for i, page in enumerate(doc, start=1):
        try:
            finder = page.find_tables()
        except Exception:
            continue
        for tbl in finder.tables:
            try:
                rows = tbl.extract()
            except Exception:
                continue
            md = _table_to_md(rows)
            if md.strip():
                out.append(TableChunk(page=i, markdown=md))
    doc.close()
    return out
