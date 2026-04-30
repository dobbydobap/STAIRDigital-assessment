"""Query rewriter (Claude Haiku): coreference resolution, decomposition, lang detection.

The rewriter never decides scope — that is reserved for the grounded-answer call,
which has the retrieved evidence in front of it.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from pdfagent.config import CONFIG
from pdfagent.llm import LLMResult, call

_SYSTEM = """You rewrite user queries to maximize retrieval recall against a single PDF.

Given the latest user message and a short conversation history, return JSON only:
{
  "language": "ISO 639-1 code, e.g. 'en', 'hi'",
  "rewritten": "self-contained version of the latest message with coreferences resolved (same language as the user)",
  "subqueries": ["1-3 short search queries in English that together cover what the user is asking; if the original is already a single concrete question, return one query"],
  "intent": "factual | definition | quantitative | summary | opinion | unclear"
}

Rules:
- Resolve pronouns and references to earlier turns ("that table", "the first author", "it") using the history.
- Decompose only if there are clearly distinct sub-questions.
- Subqueries must be in English even if the user's language is not — the document may be in any language and bge-m3 handles cross-lingual retrieval.
- Do NOT decide whether the question is answerable from the PDF.
- Output JSON only, no commentary."""


@dataclass
class RewriteResult:
    language: str
    rewritten: str
    subqueries: list[str]
    intent: str
    raw: str = ""
    usage: dict[str, Any] = field(default_factory=dict)


def _format_history(history: list[dict[str, str]]) -> str:
    if not history:
        return "(none)"
    lines = []
    for turn in history[-CONFIG.max_history_turns * 2:]:
        role = turn.get("role", "user").upper()
        content = (turn.get("content") or "").strip()
        if content:
            lines.append(f"{role}: {content}")
    return "\n".join(lines) if lines else "(none)"


def rewrite_query(query: str, history: list[dict[str, str]] | None = None) -> RewriteResult:
    history = history or []
    user = (
        f"Conversation history:\n{_format_history(history)}\n\n"
        f"Latest user message:\n{query.strip()}\n\n"
        "Return the JSON object now."
    )
    res: LLMResult = call(
        system=_SYSTEM,
        user=user,
        model=CONFIG.model_rewrite,
        max_tokens=400,
        temperature=0.0,
    )
    try:
        data = res.parse_json()
    except Exception:
        # Fallback: treat the original query as its own subquery.
        return RewriteResult(
            language="en",
            rewritten=query.strip(),
            subqueries=[query.strip()],
            intent="unclear",
            raw=res.text,
            usage={"input_tokens": res.input_tokens, "output_tokens": res.output_tokens, "cost_usd": res.cost_usd, "model": res.model},
        )

    sub = data.get("subqueries") or []
    if isinstance(sub, str):
        sub = [sub]
    sub = [str(s).strip() for s in sub if str(s).strip()]
    if not sub:
        sub = [query.strip()]

    return RewriteResult(
        language=str(data.get("language", "en")).strip().lower() or "en",
        rewritten=str(data.get("rewritten", query)).strip() or query.strip(),
        subqueries=sub,
        intent=str(data.get("intent", "unclear")).strip().lower() or "unclear",
        raw=res.text,
        usage={"input_tokens": res.input_tokens, "output_tokens": res.output_tokens, "cost_usd": res.cost_usd, "model": res.model},
    )
