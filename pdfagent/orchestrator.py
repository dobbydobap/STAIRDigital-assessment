"""End-to-end chat-turn orchestrator.

One call site: rewrite → retrieve → grounded-answer → verify → trace.
The FastAPI route, the Streamlit chat box, and the eval runner all use this.
"""
from __future__ import annotations

import time
from dataclasses import asdict, dataclass, field
from typing import Any

from pdfagent.agent.grounded_answer import AnswerOutcome, answer_grounded
from pdfagent.agent.verify import VerifyResult
from pdfagent.retrieve.hybrid import retrieve
from pdfagent.retrieve.rewrite import RewriteResult, rewrite_query
from pdfagent.trace.cost import sum_usage
from pdfagent.trace.logger import get_logger, new_turn_id
from pdfagent.types import GroundedAnswer, Retrieved


@dataclass
class TurnResult:
    turn_id: str
    pdf_id: str
    query: str
    rewrite: RewriteResult
    retrieved: list[Retrieved]
    answer: GroundedAnswer
    verification: VerifyResult
    attempts: int
    latency_ms: dict[str, float]
    usage: list[dict[str, Any]] = field(default_factory=list)
    cost_summary: dict[str, Any] = field(default_factory=dict)


def _retrieved_to_trace(rs: list[Retrieved]) -> list[dict]:
    return [
        {
            "chunk_id": r.chunk.chunk_id,
            "page": r.chunk.page,
            "section": r.chunk.section_path,
            "type": r.chunk.chunk_type,
            "dense": round(r.dense_score, 4),
            "sparse": round(r.sparse_score, 4),
            "combined": round(r.combined_score, 4),
            "preview": (r.chunk.text[:240] + "…") if len(r.chunk.text) > 240 else r.chunk.text,
        }
        for r in rs
    ]


def _answer_to_trace(a: GroundedAnswer) -> dict:
    return {
        "scope": a.scope,
        "sufficiency": a.sufficiency,
        "language": a.language,
        "answer": a.answer,
        "refusal_reason": a.refusal_reason,
        "citations": [
            {"page": c.page, "section": c.section, "quoted_span": c.quoted_span}
            for c in a.citations
        ],
    }


def _verification_to_trace(v: VerifyResult) -> dict:
    return {
        "ok": v.ok,
        "failure_summary": v.failure_summary,
        "checks": [
            {
                "page": ch.citation.page,
                "ok": ch.ok,
                "reason": ch.reason,
                "quoted_span": ch.citation.quoted_span,
            }
            for ch in v.checks
        ],
    }


def chat_turn(
    pdf_id: str,
    query: str,
    page_text_by_page: dict[int, str],
    history: list[dict[str, str]] | None = None,
    final_k: int = 5,
) -> TurnResult:
    history = history or []
    turn_id = new_turn_id()
    timings: dict[str, float] = {}
    t_total = time.perf_counter()

    t = time.perf_counter()
    rw = rewrite_query(query, history=history)
    timings["rewrite_ms"] = round((time.perf_counter() - t) * 1000, 1)

    t = time.perf_counter()
    retrieved = retrieve(
        pdf_id=pdf_id,
        queries=rw.subqueries,
        final_k=final_k,
    )
    timings["retrieve_ms"] = round((time.perf_counter() - t) * 1000, 1)

    t = time.perf_counter()
    outcome: AnswerOutcome = answer_grounded(
        question=rw.rewritten or query,
        retrieved=retrieved,
        page_text_by_page=page_text_by_page,
        history=history,
        language=rw.language,
    )
    timings["answer_ms"] = round((time.perf_counter() - t) * 1000, 1)
    timings["total_ms"] = round((time.perf_counter() - t_total) * 1000, 1)

    usage: list[dict[str, Any]] = []
    if rw.usage:
        usage.append({"step": "rewrite", **rw.usage})
    usage.extend(outcome.usage)
    cost_summary = sum_usage(usage)

    result = TurnResult(
        turn_id=turn_id,
        pdf_id=pdf_id,
        query=query,
        rewrite=rw,
        retrieved=retrieved,
        answer=outcome.answer,
        verification=outcome.verification,
        attempts=outcome.attempts,
        latency_ms=timings,
        usage=usage,
        cost_summary=cost_summary,
    )

    # Persist trace
    get_logger().write({
        "turn_id": turn_id,
        "pdf_id": pdf_id,
        "query": query,
        "rewrite": {
            "language": rw.language,
            "rewritten": rw.rewritten,
            "subqueries": rw.subqueries,
            "intent": rw.intent,
        },
        "retrieved": _retrieved_to_trace(retrieved),
        "answer": _answer_to_trace(outcome.answer),
        "verification": _verification_to_trace(outcome.verification),
        "attempts": outcome.attempts,
        "latency_ms": timings,
        "usage": usage,
        "cost_summary": cost_summary,
    })

    return result


def to_dict(turn: TurnResult) -> dict[str, Any]:
    """Serialize a TurnResult for JSON responses."""
    return {
        "turn_id": turn.turn_id,
        "pdf_id": turn.pdf_id,
        "query": turn.query,
        "rewrite": {
            "language": turn.rewrite.language,
            "rewritten": turn.rewrite.rewritten,
            "subqueries": turn.rewrite.subqueries,
            "intent": turn.rewrite.intent,
        },
        "retrieved": _retrieved_to_trace(turn.retrieved),
        "answer": _answer_to_trace(turn.answer),
        "verification": _verification_to_trace(turn.verification),
        "attempts": turn.attempts,
        "latency_ms": turn.latency_ms,
        "usage": turn.usage,
        "cost_summary": turn.cost_summary,
    }
