"""Helpers for rendering cached page images inside Streamlit citation expanders."""
from __future__ import annotations

from pathlib import Path

from pdfagent.config import CONFIG


def page_image_path(pdf_id: str, page: int) -> Path | None:
    p = CONFIG.page_image_dir / pdf_id / f"p{page:04d}.png"
    return p if p.exists() else None
