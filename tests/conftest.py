"""pytest fixtures.

Tests that hit Anthropic or download bge-m3 are gated behind the env var
`PDFAGENT_RUN_LIVE=1` so the fast unit tests run without network access.
"""
from __future__ import annotations

import os
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
EVAL_PDF = ROOT / "eval" / "sample.pdf"


def _live_enabled() -> bool:
    return os.getenv("PDFAGENT_RUN_LIVE") == "1"


@pytest.fixture
def live() -> bool:
    return _live_enabled()


@pytest.fixture
def sample_pdf() -> Path:
    if not EVAL_PDF.exists():
        pytest.skip(f"no sample PDF at {EVAL_PDF} — see eval/README")
    return EVAL_PDF


def pytest_collection_modifyitems(config, items):
    if _live_enabled():
        return
    skip_live = pytest.mark.skip(reason="set PDFAGENT_RUN_LIVE=1 to run live tests (hits Anthropic + downloads bge-m3)")
    for item in items:
        if "live" in item.keywords:
            item.add_marker(skip_live)
