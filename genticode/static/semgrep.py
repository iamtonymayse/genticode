from __future__ import annotations

import json
import os
import shutil
import subprocess
from pathlib import Path
from typing import Any, Iterable


def maybe_run_semgrep(root: Path, out_path: Path, timeout_s: int = 120, configs: Iterable[str] | None = None) -> dict | None:
    if shutil.which("semgrep") is None:
        return None
    jobs = max(1, min(4, (os.cpu_count() or 1)))
    cfgs = list(configs) if configs else ["p/python", "p/typescript"]
    cmd = ["semgrep", "--error"]
    for c in cfgs:
        cmd += ["--config", c]
    # Exclude generated and non-source paths
    excludes = [
        ".git",
        ".genticode",
        ".venv",
        "node_modules",
        "ssot",
        "images",
        "docs/templates",
        "build",
        "dist",
    ]
    for ex in excludes:
        cmd += ["--exclude", ex]

    cmd += [
        "--json",
        "--timeout",
        str(timeout_s),
        "--jobs",
        str(jobs),
        str(root),
    ]
    try:
        cp = subprocess.run(cmd, cwd=str(root), capture_output=True, text=True, check=True)
    except subprocess.CalledProcessError:
        return None
    data = json.loads(cp.stdout or "{}")
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(json.dumps(data, indent=2, sort_keys=True) + "\n")
    return data


def normalize_semgrep(data: dict) -> list[dict[str, Any]]:
    results = []
    for r in data.get("results", []) or []:
        path = r.get("path") or r.get("extra", {}).get("path")
        start = r.get("start", {}).get("line") or r.get("start", {}).get("lineStart") or 1
        end = r.get("end", {}).get("line") or start
        check_id = r.get("check_id") or r.get("extra", {}).get("check_id")
        message = r.get("extra", {}).get("message") or r.get("message") or ""
        sev = (r.get("extra", {}).get("severity") or "info").lower()
        results.append(
            {
                "file": path,
                "start": int(start),
                "end": int(end),
                "rule": str(check_id),
                "severity": sev,
                "message": message,
            }
        )
    return results
