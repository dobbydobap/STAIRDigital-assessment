"""Unit tests for chunking helpers (no PDF parsing required)."""
from __future__ import annotations

from pdfagent.ingest.chunk import _split_text


def test_split_short_text_returns_single_chunk():
    text = "Hello world."
    chunks = _split_text(text, target_chars=200, overlap_chars=20)
    assert len(chunks) == 1
    assert chunks[0][2] == "Hello world."


def test_split_long_text_overlaps():
    paragraph = ("Lorem ipsum dolor sit amet, consectetur adipiscing elit. " * 30).strip()
    chunks = _split_text(paragraph, target_chars=400, overlap_chars=80)
    assert len(chunks) >= 2
    # consecutive chunks share some overlap
    for a, b in zip(chunks, chunks[1:]):
        a_text = a[2]
        b_text = b[2]
        # the tail of `a` should appear at the head of `b` for ~overlap chars
        tail = a_text[-40:]
        assert tail.split()[0] in b_text


def test_split_prefers_paragraph_boundary():
    text = ("alpha beta " * 50) + "\n\n" + ("gamma delta " * 50)
    chunks = _split_text(text, target_chars=400, overlap_chars=40)
    # at least one boundary should land near the paragraph break
    boundaries = [c[1] for c in chunks[:-1]]
    assert any(abs(b - text.index("\n\n") - 2) < 50 for b in boundaries)
