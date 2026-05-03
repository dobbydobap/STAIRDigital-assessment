"""Google Gemini client wrapper.

We use Gemini's free-tier API (no credit card required). The wrapper exposes
the same `call()` function and `LLMResult` shape every other module already
uses, so this is the only file that knows which provider is behind the LLM.

If you ever want to swap to Anthropic, OpenAI, or a local model, replace the
body of `call()` and `_client()` and the rest of the codebase is unchanged.
"""
from __future__ import annotations

import json
import re
from dataclasses import dataclass
from functools import lru_cache
from typing import Any

from google import genai
from google.genai import types

from pdfagent.config import CONFIG

# Gemini free tier doesn't bill for the models we use; these are nominal
# values so the UI cost line stays consistent. Replace if you switch tier.
_PRICING = {
    "gemini-2.5-flash": (0.0, 0.0),
    "gemini-2.5-flash-lite": (0.0, 0.0),
    "gemini-2.0-flash": (0.0, 0.0),
    "gemini-2.0-flash-lite": (0.0, 0.0),
    "gemini-1.5-flash": (0.0, 0.0),
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
def _client() -> "genai.Client":
    if not CONFIG.google_api_key:
        raise RuntimeError(
            "GOOGLE_API_KEY is not set. Get a free key at "
            "https://aistudio.google.com/apikey and put it in .env"
        )
    return genai.Client(api_key=CONFIG.google_api_key)


def _cost(model: str, input_tokens: int, output_tokens: int) -> float:
    pin, pout = _PRICING.get(model, (0.0, 0.0))
    return (input_tokens * pin + output_tokens * pout) / 1_000_000


def call(
    *,
    system: str,
    user: str,
    model: str | None = None,
    max_tokens: int = 1024,
    temperature: float = 0.0,
) -> LLMResult:
    """Send a single-turn message to Gemini.

    `system` becomes Gemini's `system_instruction`. `user` is the message body.
    Returns text plus token counts so callers can log usage.
    """
    m = model or CONFIG.model_answer
    config = types.GenerateContentConfig(
        system_instruction=system,
        max_output_tokens=max_tokens,
        temperature=temperature,
    )
    response = _client().models.generate_content(
        model=m,
        contents=user,
        config=config,
    )
    text = (getattr(response, "text", "") or "").strip()
    usage = getattr(response, "usage_metadata", None)
    in_tok = int(getattr(usage, "prompt_token_count", 0) or 0) if usage else 0
    out_tok = int(getattr(usage, "candidates_token_count", 0) or 0) if usage else 0
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
