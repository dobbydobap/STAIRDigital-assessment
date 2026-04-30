"""Pydantic schemas for the FastAPI surface."""
from __future__ import annotations

from typing import Any, Literal

from pydantic import BaseModel, Field


class HistoryTurn(BaseModel):
    role: Literal["user", "assistant"]
    content: str


class ChatRequest(BaseModel):
    pdf_id: str
    query: str = Field(min_length=1)
    history: list[HistoryTurn] = Field(default_factory=list)
    final_k: int = 5


class CitationOut(BaseModel):
    page: int
    section: str = ""
    quoted_span: str = ""


class AnswerOut(BaseModel):
    scope: str
    sufficiency: str
    language: str
    answer: str
    refusal_reason: str | None = None
    citations: list[CitationOut]


class CitationCheckOut(BaseModel):
    page: int
    ok: bool
    reason: str = ""
    quoted_span: str = ""


class VerificationOut(BaseModel):
    ok: bool
    failure_summary: str = ""
    checks: list[CitationCheckOut] = Field(default_factory=list)


class RetrievedOut(BaseModel):
    chunk_id: str
    page: int
    section: str
    type: str
    dense: float
    sparse: float
    combined: float
    preview: str


class RewriteOut(BaseModel):
    language: str
    rewritten: str
    subqueries: list[str]
    intent: str


class ChatResponse(BaseModel):
    turn_id: str
    pdf_id: str
    query: str
    rewrite: RewriteOut
    retrieved: list[RetrievedOut]
    answer: AnswerOut
    verification: VerificationOut
    attempts: int
    latency_ms: dict[str, float]
    usage: list[dict[str, Any]]
    cost_summary: dict[str, Any]


class PdfSummary(BaseModel):
    pdf_id: str
    original_filename: str
    num_pages: int
    has_tables: bool
    has_ocr: bool


class UploadResponse(PdfSummary):
    pass


class TraceListResponse(BaseModel):
    traces: list[dict[str, Any]]
