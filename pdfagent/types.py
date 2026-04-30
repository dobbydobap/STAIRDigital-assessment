"""Shared dataclasses passed between layers."""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Literal


ChunkType = Literal["text", "table", "ocr"]


@dataclass
class Chunk:
    chunk_id: str
    pdf_id: str
    page: int
    section_path: str
    chunk_type: ChunkType
    text: str
    char_start: int = 0
    char_end: int = 0


@dataclass
class Retrieved:
    chunk: Chunk
    dense_score: float
    sparse_score: float
    combined_score: float


@dataclass
class Citation:
    page: int
    section: str
    quoted_span: str


Sufficiency = Literal["sufficient", "insufficient", "partial", "contradictory"]
Scope = Literal["in_scope", "out_of_scope"]


@dataclass
class GroundedAnswer:
    sufficiency: Sufficiency
    scope: Scope
    answer: str
    citations: list[Citation] = field(default_factory=list)
    refusal_reason: str | None = None
    language: str = "en"
