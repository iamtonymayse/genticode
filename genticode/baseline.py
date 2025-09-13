from __future__ import annotations

import json
import shutil
from pathlib import Path


def baseline_capture(gc_dir: Path) -> int:
    report_path = gc_dir / "report.json"
    base_dir = gc_dir / "baseline"
    base_dir.mkdir(parents=True, exist_ok=True)
    if report_path.exists():
        data = json.loads(report_path.read_text())
    else:
        data = {
            "schema_version": "0.1.0",
            "genticode_version": "0.1a",
            "summary": {"counts": {"total": 0}},
            "packs": [],
            "findings": [],
        }
    (base_dir / "report.json").write_text(json.dumps(data, indent=2, sort_keys=True) + "\n")
    print(str(base_dir / "report.json"))
    return 0


def baseline_clear(gc_dir: Path) -> int:
    base_dir = gc_dir / "baseline"
    if base_dir.exists():
        shutil.rmtree(base_dir)
    base_dir.mkdir(parents=True, exist_ok=True)
    print(str(base_dir))
    return 0

