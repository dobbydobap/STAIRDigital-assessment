"""Unit tests for the deterministic verbatim-quote verifier."""
from __future__ import annotations

from pdfagent.agent.verify import MIN_QUOTE_WORDS, verify_answer
from pdfagent.types import Citation


def _page_text():
    return {
        1: "The quick brown fox jumps over the lazy dog several times in this paragraph.",
        2: "Section 2 discusses the architecture of the system in considerable detail and rigor.",
    }


def test_verifier_accepts_verbatim_quote():
    cits = [Citation(page=1, section="", quoted_span="quick brown fox jumps over the lazy dog")]
    res = verify_answer(cits, _page_text())
    assert res.ok is True
    assert all(c.ok for c in res.checks)


def test_verifier_normalizes_whitespace_and_case():
    cits = [Citation(page=2, section="2", quoted_span="ARCHITECTURE   of the   System in considerable detail")]
    res = verify_answer(cits, _page_text())
    assert res.ok is True


def test_verifier_rejects_paraphrase():
    cits = [Citation(page=1, section="", quoted_span="a fast brown fox leaps over a sleeping dog")]
    res = verify_answer(cits, _page_text())
    assert res.ok is False
    assert "not found verbatim" in res.failure_summary


def test_verifier_rejects_short_quotes():
    cits = [Citation(page=1, section="", quoted_span="brown fox jumps")]
    res = verify_answer(cits, _page_text())
    assert res.ok is False
    assert "too short" in res.failure_summary


def test_verifier_requires_at_least_one_citation():
    res = verify_answer([], _page_text(), require_at_least_one=True)
    assert res.ok is False
    assert "No citations" in res.failure_summary


def test_verifier_rejects_missing_page():
    cits = [Citation(page=99, section="", quoted_span="quick brown fox jumps over the lazy dog")]
    res = verify_answer(cits, _page_text())
    assert res.ok is False
    assert "not in document" in res.failure_summary


def test_min_quote_words_constant_is_reasonable():
    assert MIN_QUOTE_WORDS >= 4
