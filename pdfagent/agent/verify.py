"""Deterministic verifier — the anti-hallucination guardrail.

For each citation the model produced, check that its `quoted_span` actually
appears (verbatim, after whitespace normalization) on the cited page. Any
citation whose quoted_span is missing or shorter than the minimum word count
fails verification.
"""
from __future__ import annotations

import re
from dataclasses import dataclass

from pdfagent.types import Citation


MIN_QUOTE_WORDS = 5  # under this a quote is too generic to be a meaningful verification


@dataclass
class CitationCheck:
    citation: Citation
    ok: bool
    reason: str = ""


@dataclass
class VerifyResult:
    ok: bool
    checks: list[CitationCheck]
    failure_summary: str = ""


_WS = re.compile(r"\s+")


def _norm(s: str) -> str:
    return _WS.sub(" ", (s or "").strip()).lower()


def _word_count(s: str) -> int:
    return len([w for w in (s or "").split() if w.strip()])


def verify_answer(
    citations: list[Citation],
    page_text_by_page: dict[int, str],
    require_at_least_one: bool = True,
) -> VerifyResult:
    """Verify each citation's quoted_span appears verbatim on its cited page."""
    checks: list[CitationCheck] = []
    failures: list[str] = []

    if require_at_least_one and not citations:
        return VerifyResult(
            ok=False,
            checks=[],
            failure_summary="No citations provided.",
        )

    for cit in citations:
        page_text = page_text_by_page.get(cit.page)
        quote = (cit.quoted_span or "").strip()
        if not quote:
            checks.append(CitationCheck(cit, False, "empty quoted_span"))
            failures.append(f"p.{cit.page}: empty quoted_span")
            continue
        if _word_count(quote) < MIN_QUOTE_WORDS:
            checks.append(CitationCheck(cit, False, f"quote too short ({_word_count(quote)} words)"))
            failures.append(f"p.{cit.page}: quote too short ({_word_count(quote)} words)")
            continue
        if not page_text:
            checks.append(CitationCheck(cit, False, f"page {cit.page} not in document"))
            failures.append(f"p.{cit.page}: page not in document")
            continue
        if _norm(quote) in _norm(page_text):
            checks.append(CitationCheck(cit, True))
        else:
            checks.append(CitationCheck(cit, False, "quote not found verbatim on cited page"))
            failures.append(f"p.{cit.page}: quote not found verbatim — {quote[:80]!r}")

    ok = all(c.ok for c in checks) and (len(checks) > 0 or not require_at_least_one)
    return VerifyResult(
        ok=ok,
        checks=checks,
        failure_summary="; ".join(failures),
    )
