"""Cheap install/config check. Run this before the live eval so you don't
burn time on a missing dependency or a typo'd API key.

    python scripts/preflight.py

Exit code 0 only if every check passes.
"""
from __future__ import annotations

import os
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def _ok(msg: str) -> None:
    print(f"  OK   {msg}")


def _fail(msg: str) -> str:
    print(f"  FAIL {msg}")
    return msg


def main() -> int:
    failures: list[str] = []
    print("preflight: checking imports …")
    for mod in ("fitz", "anthropic", "chromadb", "FlagEmbedding", "fastapi", "streamlit", "yaml", "pydantic"):
        try:
            __import__(mod)
        except Exception as e:
            failures.append(_fail(f"import {mod}: {e}"))
        else:
            _ok(f"import {mod}")

    print("preflight: checking config …")
    try:
        from pdfagent.config import CONFIG
        if not CONFIG.anthropic_api_key:
            failures.append(_fail("ANTHROPIC_API_KEY is empty (set it in .env)"))
        else:
            _ok("ANTHROPIC_API_KEY is set")
        for d in (CONFIG.chroma_dir, CONFIG.traces_dir, CONFIG.uploads_dir, CONFIG.page_image_dir):
            if d.exists():
                _ok(f"data dir present: {d}")
            else:
                failures.append(_fail(f"data dir missing: {d}"))
    except Exception as e:
        failures.append(_fail(f"loading pdfagent.config: {e}"))

    print("preflight: checking eval inputs …")
    sample = ROOT / "eval" / "sample.pdf"
    if sample.exists() and sample.stat().st_size > 0:
        _ok(f"eval/sample.pdf present ({sample.stat().st_size // 1024} KB)")
    else:
        failures.append(_fail("eval/sample.pdf missing — drop a PDF there before running the eval"))

    queries = ROOT / "eval" / "queries.yaml"
    if queries.exists():
        _ok("eval/queries.yaml present")
    else:
        failures.append(_fail("eval/queries.yaml missing"))

    if failures:
        print(f"\npreflight: {len(failures)} failure(s).")
        return 1
    print("\npreflight: all checks passed.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
