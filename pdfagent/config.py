"""Centralised runtime config. Reads env once; modules import the singleton."""
from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path

from dotenv import load_dotenv

load_dotenv()


@dataclass(frozen=True)
class Config:
    google_api_key: str
    data_dir: Path
    model_answer: str
    model_rewrite: str
    max_history_turns: int

    @property
    def chroma_dir(self) -> Path:
        return self.data_dir / "chroma"

    @property
    def traces_dir(self) -> Path:
        return self.data_dir / "traces"

    @property
    def uploads_dir(self) -> Path:
        return self.data_dir / "uploads"

    @property
    def page_image_dir(self) -> Path:
        return self.data_dir / "page_images"


def _build() -> Config:
    data_dir = Path(os.getenv("PDFAGENT_DATA_DIR", "./data")).resolve()
    cfg = Config(
        google_api_key=os.getenv("GOOGLE_API_KEY", ""),
        data_dir=data_dir,
        model_answer=os.getenv("PDFAGENT_MODEL_ANSWER", "gemini-2.5-flash"),
        model_rewrite=os.getenv("PDFAGENT_MODEL_REWRITE", "gemini-2.5-flash-lite"),
        max_history_turns=int(os.getenv("PDFAGENT_MAX_HISTORY_TURNS", "2")),
    )
    for d in (cfg.chroma_dir, cfg.traces_dir, cfg.uploads_dir, cfg.page_image_dir):
        d.mkdir(parents=True, exist_ok=True)
    return cfg


CONFIG = _build()
