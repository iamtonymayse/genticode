from __future__ import annotations

import json
import shutil
import subprocess
from pathlib import Path


def _run_cmd(cmd: list[str], cwd: Path) -> list[dict]:
    try:
        cp = subprocess.run(cmd, cwd=str(cwd), capture_output=True, text=True, check=False)
        data = json.loads(cp.stdout or "[]")
        return data if isinstance(data, list) else []
    except Exception:
        return []


def maybe_run_quality(root: Path) -> dict:
    """Return normalized counts from available linters (ruff/eslint)."""
    counts = {"findings": 0}
    # ruff (JSON): ruff check --output-format json
    if shutil.which("ruff") is not None:
        data = _run_cmd(["ruff", "check", "--output-format", "json", str(root)], root)
        counts["findings"] += len(data)
    # eslint (JSON): eslint -f json .
    if shutil.which("eslint") is not None:
        data = _run_cmd(["eslint", "-f", "json", "."], root)
        # Sum up messages
        total = 0
        for f in data:
            total += len(f.get("messages", []) or [])
        counts["findings"] += int(total)
    return counts

