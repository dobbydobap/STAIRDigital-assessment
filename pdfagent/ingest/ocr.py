"""OCR fallback for image-only pages, lazy-loaded."""
from __future__ import annotations

import io
from functools import lru_cache

import fitz


@lru_cache(maxsize=1)
def _engine():
    from rapidocr_onnxruntime import RapidOCR
    return RapidOCR()


def ocr_page(pdf_path: str, page_number: int, dpi: int = 200) -> str:
    """Run OCR on a single page (1-indexed). Returns concatenated text."""
    doc = fitz.open(pdf_path)
    try:
        page = doc[page_number - 1]
        pix = page.get_pixmap(dpi=dpi)
        png_bytes = pix.tobytes("png")
    finally:
        doc.close()

    engine = _engine()
    result, _ = engine(png_bytes)
    if not result:
        return ""
    lines = [str(item[1]) for item in result if item and len(item) >= 2]
    return "\n".join(lines)
