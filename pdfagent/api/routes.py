"""HTTP routes — thin wrappers around `pdfagent.service`."""
from __future__ import annotations

import shutil
import sys
import tempfile
from pathlib import Path

# `eval/` is a top-level project directory (not part of the installed
# pdfagent package), so add the project root to sys.path before the
# `from eval.run_eval import run_eval` inside the /eval route.
_PROJECT_ROOT = str(Path(__file__).resolve().parents[2])
if _PROJECT_ROOT not in sys.path:
    sys.path.insert(0, _PROJECT_ROOT)

from fastapi import APIRouter, File, HTTPException, Query, UploadFile
from fastapi.responses import FileResponse, JSONResponse

from pdfagent.api.schemas import (
    ChatRequest,
    ChatResponse,
    PdfSummary,
    TraceListResponse,
    UploadResponse,
)
from pdfagent.config import CONFIG
from pdfagent.orchestrator import to_dict
from pdfagent.registry import get_registry
from pdfagent.service import chat, ingest_and_index
from pdfagent.trace.logger import read_traces

router = APIRouter()


@router.get("/health")
def health() -> dict:
    return {"status": "ok"}


@router.post("/upload", response_model=UploadResponse)
async def upload_pdf(file: UploadFile = File(...)) -> UploadResponse:
    if not file.filename or not file.filename.lower().endswith(".pdf"):
        raise HTTPException(400, "file must be a .pdf")

    # Stream upload to a temp file so the ingest pipeline can hash it.
    with tempfile.NamedTemporaryFile(suffix=".pdf", delete=False) as tmp:
        shutil.copyfileobj(file.file, tmp)
        tmp_path = Path(tmp.name)
    try:
        rec = ingest_and_index(tmp_path, original_filename=file.filename)
    finally:
        try:
            tmp_path.unlink(missing_ok=True)
        except Exception:
            pass

    return UploadResponse(
        pdf_id=rec.pdf_id,
        original_filename=rec.original_filename,
        num_pages=rec.num_pages,
        has_tables=rec.has_tables,
        has_ocr=rec.has_ocr,
    )


@router.get("/pdfs", response_model=list[PdfSummary])
def list_pdfs() -> list[PdfSummary]:
    out = []
    for rec in get_registry().list_records():
        out.append(PdfSummary(
            pdf_id=rec.pdf_id,
            original_filename=rec.original_filename,
            num_pages=rec.num_pages,
            has_tables=rec.has_tables,
            has_ocr=rec.has_ocr,
        ))
    return out


@router.post("/chat", response_model=ChatResponse)
def chat_route(req: ChatRequest) -> JSONResponse:
    try:
        turn = chat(
            pdf_id=req.pdf_id,
            query=req.query,
            history=[h.model_dump() for h in req.history],
            final_k=req.final_k,
        )
    except KeyError as e:
        raise HTTPException(404, str(e))
    return JSONResponse(to_dict(turn))


@router.get("/page-image/{pdf_id}/{page}")
def page_image(pdf_id: str, page: int) -> FileResponse:
    rec = get_registry().get(pdf_id)
    if rec is None:
        raise HTTPException(404, "pdf_id not found")
    if page < 1 or page > rec.num_pages:
        raise HTTPException(400, f"page must be 1..{rec.num_pages}")
    p = CONFIG.page_image_dir / pdf_id / f"p{page:04d}.png"
    if not p.exists():
        raise HTTPException(404, "page image not cached")
    return FileResponse(p, media_type="image/png")


@router.get("/traces", response_model=TraceListResponse)
def traces(limit: int = Query(50, ge=1, le=500)) -> TraceListResponse:
    return TraceListResponse(traces=read_traces(limit=limit))


@router.post("/eval")
def run_eval_route() -> dict:
    from eval.run_eval import run_eval
    report = run_eval()
    return report
