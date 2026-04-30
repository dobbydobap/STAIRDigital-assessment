"""Single Sonnet call that produces a grounded answer + citations as JSON.

If the deterministic verifier rejects the answer, we regenerate ONCE with the
failure as feedback. A second failure becomes a 'verification_failed' refusal
rather than risking a hallucinated answer.
"""
from __future__ import annotations

import json
from dataclasses import dataclass, field
from typing import Any

from pdfagent.agent.prompts import (
    GROUNDED_SYSTEM,
    GROUNDED_USER_TEMPLATE,
    format_evidence_block,
    format_history_block,
)
from pdfagent.agent.verify import VerifyResult, verify_answer
from pdfagent.config import CONFIG
from pdfagent.llm import call
from pdfagent.types import Citation, GroundedAnswer, Retrieved


@dataclass
class AnswerOutcome:
    answer: GroundedAnswer
    verification: VerifyResult
    attempts: int
    raw_responses: list[str] = field(default_factory=list)
    usage: list[dict[str, Any]] = field(default_factory=list)


def _coerce_citations(raw_cits: Any) -> list[Citation]:
    out: list[Citation] = []
    if not isinstance(raw_cits, list):
        return out
    for c in raw_cits:
        if not isinstance(c, dict):
            continue
        try:
            page = int(c.get("page", 0))
        except (TypeError, ValueError):
            continue
        if page <= 0:
            continue
        out.append(
            Citation(
                page=page,
                section=str(c.get("section") or ""),
                quoted_span=str(c.get("quoted_span") or ""),
            )
        )
    return out


def _parse(payload: dict[str, Any], fallback_lang: str) -> GroundedAnswer:
    scope = str(payload.get("scope", "in_scope")).lower()
    if scope not in ("in_scope", "out_of_scope"):
        scope = "in_scope"
    sufficiency = str(payload.get("sufficiency", "insufficient")).lower()
    if sufficiency not in ("sufficient", "partial", "insufficient", "contradictory"):
        sufficiency = "insufficient"
    answer_text = str(payload.get("answer") or "")
    refusal = payload.get("refusal_reason")
    if refusal is not None:
        refusal = str(refusal)
    citations = _coerce_citations(payload.get("citations"))
    language = str(payload.get("language") or fallback_lang or "en").lower()[:5]
    return GroundedAnswer(
        sufficiency=sufficiency,  # type: ignore[arg-type]
        scope=scope,  # type: ignore[arg-type]
        answer=answer_text,
        citations=citations,
        refusal_reason=refusal,
        language=language,
    )


def _make_user(question: str, history: list[dict[str, str]], retrieved: list[Retrieved], language: str) -> str:
    return GROUNDED_USER_TEMPLATE.format(
        language=language,
        question=question.strip(),
        history_block=format_history_block(history),
        evidence_block=format_evidence_block(retrieved),
    )


def answer_grounded(
    question: str,
    retrieved: list[Retrieved],
    page_text_by_page: dict[int, str],
    history: list[dict[str, str]] | None = None,
    language: str = "en",
    max_attempts: int = 2,
) -> AnswerOutcome:
    history = history or []
    raw_responses: list[str] = []
    usage: list[dict[str, Any]] = []
    last_answer: GroundedAnswer | None = None
    last_verify: VerifyResult | None = None
    feedback: str | None = None

    for attempt in range(1, max_attempts + 1):
        user = _make_user(question, history, retrieved, language)
        if feedback:
            user = (
                f"{user}\n\nPREVIOUS ATTEMPT FAILED VERIFICATION: {feedback}\n"
                "Re-read the EVIDENCE and produce a corrected JSON. "
                "Use only verbatim 8–25 word spans that actually appear in EVIDENCE; "
                "if you cannot find a verbatim span for a claim, drop the claim or set sufficiency=insufficient."
            )
        res = call(
            system=GROUNDED_SYSTEM,
            user=user,
            model=CONFIG.model_answer,
            max_tokens=1500,
            temperature=0.0,
        )
        raw_responses.append(res.text)
        usage.append({
            "step": f"grounded_answer_attempt_{attempt}",
            "model": res.model,
            "input_tokens": res.input_tokens,
            "output_tokens": res.output_tokens,
            "cost_usd": res.cost_usd,
        })
        try:
            payload = res.parse_json()
        except Exception as e:
            feedback = f"Previous response was not valid JSON ({e})."
            continue

        ans = _parse(payload, language)

        # Refusals do not need quote verification.
        if ans.scope == "out_of_scope" or ans.sufficiency == "insufficient":
            return AnswerOutcome(
                answer=ans,
                verification=VerifyResult(ok=True, checks=[], failure_summary=""),
                attempts=attempt,
                raw_responses=raw_responses,
                usage=usage,
            )

        verify = verify_answer(
            citations=ans.citations,
            page_text_by_page=page_text_by_page,
            require_at_least_one=True,
        )
        last_answer, last_verify = ans, verify
        if verify.ok:
            return AnswerOutcome(
                answer=ans,
                verification=verify,
                attempts=attempt,
                raw_responses=raw_responses,
                usage=usage,
            )
        feedback = verify.failure_summary

    # Both attempts failed verification — return a verification-failed refusal.
    refusal = GroundedAnswer(
        sufficiency="insufficient",
        scope="in_scope",
        answer="",
        citations=last_answer.citations if last_answer else [],
        refusal_reason=(
            "I could not produce an answer whose quotes I could verify against the document. "
            f"Verifier said: {last_verify.failure_summary if last_verify else 'unknown'}. "
            "Try asking more specifically (e.g. naming a section, table, or page)."
        ),
        language=language,
    )
    return AnswerOutcome(
        answer=refusal,
        verification=last_verify or VerifyResult(ok=False, checks=[], failure_summary="no verification"),
        attempts=max_attempts,
        raw_responses=raw_responses,
        usage=usage,
    )
