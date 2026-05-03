"""Groq client wrapper.

We use Groq's free-tier API (no credit card required). The wrapper exposes
the same `call()` function and `LLMResult` shape every other module already
uses, so this is the only file that knows which provider is behind the LLM.

If you ever want to swap to Gemini, Anthropic, OpenAI, or a local model,
replace the body of `call()` and `_client()` and the rest of the codebase
is unchanged. (Prior Anthropic/Gemini adapters are preserved in git history.)
"""
from __future__ import annotations

import json
import re
import time
from dataclasses import dataclass
from functools import lru_cache
from typing import Any

from groq import APIConnectionError, APITimeoutError, Groq, RateLimitError

from pdfagent.config import CONFIG

_MAX_RETRIES = 3
_RETRY_BACKOFF_SEC = (1.0, 3.0, 8.0)  # exponential pause before retry n

# Groq's free tier doesn't bill — these placeholders keep the UI cost line
# consistent. Update if you switch to a paid tier.
_PRICING = {
    "llama-3.3-70b-versatile": (0.0, 0.0),
    "llama-3.1-70b-versatile": (0.0, 0.0),
    "llama-3.1-8b-instant": (0.0, 0.0),
    "llama-3.2-90b-text-preview": (0.0, 0.0),
    "mixtral-8x7b-32768": (0.0, 0.0),
    "gemma2-9b-it": (0.0, 0.0),
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
def _client() -> Groq:
    if not CONFIG.groq_api_key:
        raise RuntimeError(
            "GROQ_API_KEY is not set. Get a free key at "
            "https://console.groq.com/keys and put it in .env"
        )
    # max_retries is the SDK's built-in retry on 5xx / rate-limit; we add our
    # own loop in `call()` for transient connection failures.
    return Groq(api_key=CONFIG.groq_api_key, max_retries=2)


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
    """Single-turn call to Groq.

    Retries automatically on transient `APIConnectionError`, `APITimeoutError`,
    and `RateLimitError` so flaky networks and free-tier rate-limit dips don't
    bubble up as fatal errors during the eval or live demo.
    """
    m = model or CONFIG.model_answer
    last_err: Exception | None = None
    for attempt in range(_MAX_RETRIES):
        try:
            response = _client().chat.completions.create(
                model=m,
                messages=[
                    {"role": "system", "content": system},
                    {"role": "user", "content": user},
                ],
                max_tokens=max_tokens,
                temperature=temperature,
            )
            text = (response.choices[0].message.content or "").strip()
            usage = response.usage
            in_tok = int(getattr(usage, "prompt_tokens", 0) or 0)
            out_tok = int(getattr(usage, "completion_tokens", 0) or 0)
            return LLMResult(
                text=text,
                model=m,
                input_tokens=in_tok,
                output_tokens=out_tok,
                cost_usd=_cost(m, in_tok, out_tok),
            )
        except (APIConnectionError, APITimeoutError, RateLimitError) as e:
            last_err = e
            if attempt < _MAX_RETRIES - 1:
                time.sleep(_RETRY_BACKOFF_SEC[attempt])
                continue
            break
    assert last_err is not None
    raise last_err


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
