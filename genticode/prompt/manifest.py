from __future__ import annotations

import json
import re
from dataclasses import asdict
from pathlib import Path
from typing import Iterable

from .detect import PromptSpan


_URL_RE = re.compile(r"https?://\S{80,}")


def _lint_codes(text: str) -> list[str]:
    codes: list[str] = []
    # Missing ID / version stamps (heuristic)
    if "PROMPT_ID:" not in text:
        codes.append("PROMPT_MISSING_ID")
    if not re.search(r"\bv\d+\b", text, re.I):
        codes.append("PROMPT_MISSING_VERSION")
    # Secret placeholders / tokens
    if re.search(r"\b(ghp_[A-Za-z0-9]{20,}|github_pat_[A-Za-z0-9_]{20,}|sk-[A-Za-z0-9]{20,})\b", text):
        codes.append("SECRET_PLACEHOLDER")
    # Long opaque URLs
    if _URL_RE.search(text):
        codes.append("LONG_URL")
    return codes


def build_manifest(spans: Iterable[PromptSpan]) -> dict:
    items = []
    for s in spans:
        entry = {
            "id": s.id,
            "file": str(s.file),
            "start": s.start,
            "end": s.end,
            "role": s.role,
            "version": "v1",
            "source_hash": s.id,
            "lints": _lint_codes(s.text),
        }
        items.append(entry)
    return {"schema": "prompt-manifest/0.1", "items": items}


def write_manifest(path: Path, manifest: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(manifest, indent=2, sort_keys=True) + "\n")

