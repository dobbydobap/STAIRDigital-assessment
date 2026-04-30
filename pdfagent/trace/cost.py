"""Aggregate per-turn cost helpers shown in the UI footer."""
from __future__ import annotations

from typing import Iterable


def sum_usage(usage_records: Iterable[dict]) -> dict:
    total_in = 0
    total_out = 0
    total_cost = 0.0
    by_model: dict[str, dict] = {}
    for u in usage_records or []:
        m = u.get("model", "unknown")
        i = int(u.get("input_tokens", 0))
        o = int(u.get("output_tokens", 0))
        c = float(u.get("cost_usd", 0.0))
        total_in += i
        total_out += o
        total_cost += c
        bm = by_model.setdefault(m, {"input_tokens": 0, "output_tokens": 0, "cost_usd": 0.0})
        bm["input_tokens"] += i
        bm["output_tokens"] += o
        bm["cost_usd"] += c
    return {
        "input_tokens": total_in,
        "output_tokens": total_out,
        "cost_usd": round(total_cost, 6),
        "by_model": by_model,
    }
