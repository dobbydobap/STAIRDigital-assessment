"""PDF registry — small JSON-on-disk store mapping pdf_id to its metadata
and the per-page text needed by the verifier. Lives next to the Chroma DB.
"""
from __future__ import annotations

import json
import threading
from dataclasses import asdict, dataclass, field
from functools import lru_cache
from pathlib import Path
from typing import Any

from pdfagent.config import CONFIG


@dataclass
class PdfRecord:
    pdf_id: str
    original_filename: str
    pdf_path: str
    num_pages: int
    page_text_by_page: dict[int, str] = field(default_factory=dict)
    has_tables: bool = False
    has_ocr: bool = False
    languages_detected: list[str] = field(default_factory=list)


class Registry:
    def __init__(self, base_dir: Path | None = None) -> None:
        self.dir = (base_dir or CONFIG.data_dir) / "pdfs"
        self.dir.mkdir(parents=True, exist_ok=True)
        self._lock = threading.Lock()
        self._cache: dict[str, PdfRecord] = {}

    def _path(self, pdf_id: str) -> Path:
        return self.dir / f"{pdf_id}.json"

    def upsert(self, rec: PdfRecord) -> None:
        with self._lock:
            payload = asdict(rec)
            payload["page_text_by_page"] = {str(k): v for k, v in rec.page_text_by_page.items()}
            self._path(rec.pdf_id).write_text(
                json.dumps(payload, ensure_ascii=False), encoding="utf-8"
            )
            self._cache[rec.pdf_id] = rec

    def get(self, pdf_id: str) -> PdfRecord | None:
        with self._lock:
            if pdf_id in self._cache:
                return self._cache[pdf_id]
            p = self._path(pdf_id)
            if not p.exists():
                return None
            data = json.loads(p.read_text(encoding="utf-8"))
            page_text = {int(k): v for k, v in (data.get("page_text_by_page") or {}).items()}
            data["page_text_by_page"] = page_text
            rec = PdfRecord(**data)
            self._cache[pdf_id] = rec
            return rec

    def list_records(self) -> list[PdfRecord]:
        out: list[PdfRecord] = []
        for p in sorted(self.dir.glob("*.json")):
            rec = self.get(p.stem)
            if rec:
                out.append(rec)
        return out


@lru_cache(maxsize=1)
def get_registry() -> Registry:
    return Registry()
