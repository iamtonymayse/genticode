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
    """Return normalized counts from available linters (ruff/eslint).

    Produces counts.findings and counts.by_severity mapping.
    """
    counts = {"findings": 0, "by_severity": {}}

    def bump(sev: str, n: int = 1):
        sev = sev.lower()
        m = counts["by_severity"]
        m[sev] = int(m.get(sev, 0)) + int(n)

    # ruff (JSON): ruff check --output-format json
    if shutil.which("ruff") is not None:
        data = _run_cmd(["ruff", "check", "--output-format", "json", str(root)], root)
        # Treat ruff items as warnings by default
        n = len(data)
        counts["findings"] += n
        if n:
            bump("warning", n)
    # eslint (JSON): eslint -f json .
    if shutil.which("eslint") is not None:
        data = _run_cmd(["eslint", "-f", "json", "."], root)
        # Sum up messages
        total = 0
        for f in data:
            msgs = f.get("messages", []) or []
            total += len(msgs)
            for m in msgs:
                sev = int(m.get("severity", 1))
                bump("error" if sev == 2 else "warning", 1)
        counts["findings"] += int(total)
    return counts
