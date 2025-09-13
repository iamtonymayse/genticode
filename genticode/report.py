from __future__ import annotations

import json
import platform
from pathlib import Path


def build_empty_report(version: str, baseline_present: bool) -> dict:
    return {
        "schema_version": "0.1.0",
        "genticode_version": version,
        "summary": {"counts": {"total": 0}},
        "packs": [],
        "findings": [],
        "baseline": {"present": bool(baseline_present)},
        "environment": {
            "platform": platform.system(),
            "python": platform.python_version(),
        },
    }


def write_json(path: Path, data: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, indent=2, sort_keys=True) + "\n")


def add_pack_summary(report: dict, pack: str, counts: dict) -> None:
    packs = report.setdefault("packs", [])
    packs.append({"name": pack, "counts": counts})
