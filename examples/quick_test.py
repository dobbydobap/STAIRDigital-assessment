"""Programmatic example: ingest one PDF, ask one question, print the result.

    python examples/quick_test.py path/to/your.pdf "What is this document about?"

Useful for evaluators who want to sanity-check the agent without launching
the UI or running the full eval suite.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

from pdfagent.orchestrator import to_dict
from pdfagent.service import chat as svc_chat, ingest_and_index


def main() -> int:
    if len(sys.argv) < 3:
        print("usage: python examples/quick_test.py <pdf_path> <question>", file=sys.stderr)
        return 2
    pdf = Path(sys.argv[1])
    question = " ".join(sys.argv[2:])
    if not pdf.exists():
        print(f"PDF not found: {pdf}", file=sys.stderr)
        return 2

    print(f"ingesting {pdf} …")
    rec = ingest_and_index(pdf, original_filename=pdf.name)
    print(f"  pdf_id={rec.pdf_id}  pages={rec.num_pages}  tables={rec.has_tables}  ocr={rec.has_ocr}")

    print(f"\nasking: {question}")
    turn = svc_chat(pdf_id=rec.pdf_id, query=question)
    td = to_dict(turn)

    ans = td["answer"]
    print(f"\nscope:        {ans['scope']}")
    print(f"sufficiency:  {ans['sufficiency']}")
    print(f"language:     {ans['language']}")
    print(f"verifier ok:  {td['verification']['ok']}")
    if ans["answer"]:
        print(f"\nanswer:\n{ans['answer']}")
    if ans.get("refusal_reason"):
        print(f"\nrefusal_reason: {ans['refusal_reason']}")
    if ans.get("citations"):
        print("\ncitations:")
        for c in ans["citations"]:
            print(f"  p.{c['page']} §{c['section'] or '—'}: \"{c['quoted_span']}\"")
    print(f"\nlatency: {td['latency_ms']}")
    print(f"cost:    ~${td['cost_summary'].get('cost_usd', 0):.4f}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
