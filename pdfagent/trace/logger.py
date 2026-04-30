"""JSONL-per-day trace logger. One line per chat turn.

The trace captures the full agent pipeline so the UI's /traces page can
explain exactly what happened on any turn: rewrite, retrieval scores,
sufficiency verdict, citation verifier results, per-step latency, tokens.
"""
from __future__ import annotations

import datetime as _dt
import json
import threading
import uuid
from functools import lru_cache
from pathlib import Path
from typing import Any, Iterable

from pdfagent.config import CONFIG


def new_turn_id() -> str:
    return uuid.uuid4().hex[:12]


class TraceLogger:
    def __init__(self, traces_dir: str | Path | None = None) -> None:
        self.dir = Path(traces_dir or CONFIG.traces_dir)
        self.dir.mkdir(parents=True, exist_ok=True)
        self._lock = threading.Lock()

    def _path_for_today(self) -> Path:
        day = _dt.datetime.utcnow().strftime("%Y-%m-%d")
        return self.dir / f"traces-{day}.jsonl"

    def write(self, record: dict[str, Any]) -> None:
        record = {**record, "logged_at": _dt.datetime.utcnow().isoformat() + "Z"}
        line = json.dumps(record, ensure_ascii=False, default=str)
        path = self._path_for_today()
        with self._lock, path.open("a", encoding="utf-8") as f:
            f.write(line + "\n")

    def list_files(self) -> list[Path]:
        return sorted(self.dir.glob("traces-*.jsonl"), reverse=True)


def read_traces(limit: int = 50, files: Iterable[Path] | None = None) -> list[dict[str, Any]]:
    """Read the most recent `limit` trace records, newest first."""
    logger = get_logger()
    paths = list(files) if files is not None else logger.list_files()
    out: list[dict[str, Any]] = []
    for p in paths:
        try:
            with p.open("r", encoding="utf-8") as f:
                for line in f:
                    line = line.strip()
                    if not line:
                        continue
                    try:
                        out.append(json.loads(line))
                    except Exception:
                        continue
        except FileNotFoundError:
            continue
    out.sort(key=lambda r: r.get("logged_at", ""), reverse=True)
    return out[:limit]


@lru_cache(maxsize=1)
def get_logger() -> TraceLogger:
    return TraceLogger()
