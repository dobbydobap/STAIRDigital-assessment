"""JSON extraction from model responses."""
from __future__ import annotations

import pytest

from pdfagent.llm import _extract_json


def test_extracts_plain_json():
    out = _extract_json('{"a": 1, "b": "x"}')
    assert out == {"a": 1, "b": "x"}


def test_extracts_fenced_json():
    txt = 'here is the json:\n```json\n{"k": [1,2,3]}\n```\n'
    assert _extract_json(txt) == {"k": [1, 2, 3]}


def test_extracts_json_embedded_in_prose():
    txt = "Sure thing — {\"scope\": \"in_scope\", \"sufficiency\": \"sufficient\"} done."
    out = _extract_json(txt)
    assert out["scope"] == "in_scope"
    assert out["sufficiency"] == "sufficient"


def test_raises_on_no_json():
    with pytest.raises(ValueError):
        _extract_json("no json anywhere here")
