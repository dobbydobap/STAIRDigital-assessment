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
    """When the paragraph break falls within the splitter's search window
    (start + 0.5*target_chars … end), it should be preferred over a plain
    whitespace boundary."""
    text = ("alpha beta " * 50) + "\n\n" + ("gamma delta " * 50)
    # target_chars must be large enough that the \n\n at offset 550 falls
    # inside the first chunk's search window [275 … 700].
    chunks = _split_text(text, target_chars=700, overlap_chars=50)
    boundaries = [c[1] for c in chunks[:-1]]
    para_end = text.index("\n\n") + 2
    assert any(abs(b - para_end) < 50 for b in boundaries), (
        f"no chunk boundary landed near the paragraph break at {para_end}; "
        f"got boundaries {boundaries}"
    )
