"""Live integration test — runs the full 8-query suite end-to-end.

Skipped unless PDFAGENT_RUN_LIVE=1 is set. Requires:
- GROQ_API_KEY in the environment (free at https://console.groq.com/keys)
- bge-m3 model downloaded (first run takes a few minutes)
- A sample PDF at eval/sample.pdf
"""
from __future__ import annotations

import pytest

pytestmark = pytest.mark.live


def test_full_eval_suite_passes(sample_pdf):  # noqa: ARG001 — sample_pdf fixture forces skip if absent
    from eval.run_eval import run_eval

    report = run_eval()
    failures = [r for r in report["results"] if not r["ok"]]
    assert not failures, "Eval failures:\n" + "\n".join(
        f"  {r['id']} ({r['category']}): expected={r['expected_behavior']} observed={r['observed']}"
        for r in failures
    )
    in_scope_with_cit = [
        r for r in report["results"]
        if r["type"] == "in_scope" and (r.get("answer") or {}).get("citations")
    ]
    assert len(in_scope_with_cit) >= 4, "expected at least 4 of 5 in-scope queries to produce citations"


def test_oos_queries_produce_refusal_reason():
    from eval.run_eval import run_eval

    report = run_eval()
    for r in report["results"]:
        if r["type"] == "out_of_scope":
            ans = r.get("answer") or {}
            assert ans.get("refusal_reason"), f"{r['id']} did not produce a refusal reason"
            assert not ans.get("answer"), f"{r['id']} produced an answer for an OOS query"
