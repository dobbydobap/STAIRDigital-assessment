"""Anthropic client wrapper. Centralizes the API key, model selection, and
returns both content and usage so callers can log tokens/cost.

Pricing table is approximate and only used for the in-UI cost counter.
"""
from __future__ import annotations

import json
import re
from dataclasses import dataclass
from functools import lru_cache
from typing import Any

import anthropic

from pdfagent.config import CONFIG

# USD per million tokens (approximate; UI shows this as an estimate).
_PRICING = {
    "claude-sonnet-4-6": (3.0, 15.0),
    "claude-opus-4-7": (15.0, 75.0),
    "claude-haiku-4-5-20251001": (1.0, 5.0),
    "claude-haiku-4-5": (1.0, 5.0),
}


@dataclass
class LLMResult:
    text: str
    model: str
    input_tokens: int
    output_tokens: int
    cost_usd: float

    def parse_json(self) -> dict[str, Any]:
        return _extract_json(self.text)


@lru_cache(maxsize=1)
def _client() -> anthropic.Anthropic:
    if not CONFIG.anthropic_api_key:
        raise RuntimeError("ANTHROPIC_API_KEY is not set; copy .env.example to .env")
    return anthropic.Anthropic(api_key=CONFIG.anthropic_api_key)


def _cost(model: str, input_tokens: int, output_tokens: int) -> float:
    pin, pout = _PRICING.get(model, (3.0, 15.0))
    return (input_tokens * pin + output_tokens * pout) / 1_000_000


def call(
    *,
    system: str,
    user: str,
    model: str | None = None,
    max_tokens: int = 1024,
    temperature: float = 0.0,
) -> LLMResult:
    m = model or CONFIG.model_answer
    resp = _client().messages.create(
        model=m,
        max_tokens=max_tokens,
        temperature=temperature,
        system=system,
        messages=[{"role": "user", "content": user}],
    )
    text_parts = [b.text for b in resp.content if getattr(b, "type", None) == "text"]
    text = "".join(text_parts).strip()
    usage = resp.usage
    in_tok = int(getattr(usage, "input_tokens", 0))
    out_tok = int(getattr(usage, "output_tokens", 0))
    return LLMResult(
        text=text,
        model=m,
        input_tokens=in_tok,
        output_tokens=out_tok,
        cost_usd=_cost(m, in_tok, out_tok),
    )


_FENCE = re.compile(r"```(?:json)?\s*(.*?)\s*```", re.DOTALL)


def _extract_json(text: str) -> dict[str, Any]:
    """Best-effort JSON extraction from a model response."""
    if not text:
        raise ValueError("empty model response")
    candidates: list[str] = []
    m = _FENCE.search(text)
    if m:
        candidates.append(m.group(1))
    candidates.append(text)
    # also try slicing from the first { to the last }
    first = text.find("{")
    last = text.rfind("}")
    if first != -1 and last != -1 and last > first:
        candidates.append(text[first:last + 1])

    for c in candidates:
        try:
            return json.loads(c)
        except Exception:
            continue
    raise ValueError(f"could not parse JSON from response: {text[:200]}")
