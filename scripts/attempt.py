#!/usr/bin/env python3
from __future__ import annotations

import json
import os
import re
import subprocess
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, Tuple


ATTEMPTS_DIR = Path(".genticode/local/attempts")
REPORTS_DIR = Path(".genticode/reports")
RAW_JSON = Path(".genticode/raw/pytest.json")


def run_pytest() -> int:
    cmd = [
        "pytest",
        "-q",
        "--maxfail=0",
        "--disable-warnings",
        "--timeout=30",
        "--cov",
        "--cov-branch",
        "--cov-fail-under=95",
        "--json-report",
        f"--json-report-file={RAW_JSON}",
    ]
    proc = subprocess.run(cmd, text=True)
    return int(proc.returncode)


def read_pytest_json(path: Path) -> dict:
    if not path.exists():
        return {}
    return json.loads(path.read_text() or "{}")


def group_failures(pytest_json: dict) -> Dict[str, list[dict]]:
    """Group failures into categories.
    Categories: Requirements|Design|Code|Test|Tooling|Environment
    Heuristic: default to Code; if message mentions 'timeout' -> Environment; if ImportError -> Tooling; if AssertionError -> Test.
    """
    cats = {k: [] for k in ["Requirements", "Design", "Code", "Test", "Tooling", "Environment"]}
    tests = (pytest_json.get("tests") or [])
    for t in tests:
        if t.get("outcome") == "failed":
            msg = (t.get("call", {}) or {}).get("longrepr", "")
            m = msg.lower()
            if "timeout" in m:
                cats["Environment"].append(t)
            elif "importerror" in m or "module not found" in m:
                cats["Tooling"].append(t)
            elif "assert" in m or "assertionerror" in m:
                cats["Test"].append(t)
            else:
                cats["Code"].append(t)
    # Prune empty
    return {k: v for k, v in cats.items() if v}


def next_attempt_index(dir: Path) -> int:
    dir.mkdir(parents=True, exist_ok=True)
    idx = 1
    for p in dir.glob("attempt-*.json"):
        try:
            n = int(p.stem.split("-")[-1])
            if n >= idx:
                idx = n + 1
        except Exception:
            pass
    return idx


def write_attempt(index: int, summary: dict) -> Tuple[Path, Path]:
    ATTEMPTS_DIR.mkdir(parents=True, exist_ok=True)
    REPORTS_DIR.mkdir(parents=True, exist_ok=True)
    jpath = ATTEMPTS_DIR / f"attempt-{index}.json"
    mpath = REPORTS_DIR / f"attempt-{index}.md"
    jpath.write_text(json.dumps(summary, indent=2, sort_keys=True) + "\n")
    # markdown summary
    md = [f"# Attempt {index}"]
    md.append(f"Exit code: {summary.get('exit_code')}")
    md.append("## Failure groups")
    groups = summary.get("groups", {})
    if groups:
        for k, v in groups.items():
            md.append(f"- {k}: {len(v)}")
    else:
        md.append("- none")
    md.append("\nEnvironment")
    env = summary.get("env", {})
    if env:
        for k, v in env.items():
            md.append(f"- {k}: {v}")
    mpath.write_text("\n".join(md) + "\n")
    return jpath, mpath


def build_summary(exit_code: int, pytest_json: dict) -> dict:
    import platform

    groups = group_failures(pytest_json)
    return {
        "exit_code": int(exit_code),
        "groups": groups,
        "counts": {k: len(v) for k, v in groups.items()},
        "env": {"python": platform.python_version(), "platform": platform.system()},
    }


def main() -> int:
    rc = run_pytest()
    data = read_pytest_json(RAW_JSON)
    summary = build_summary(rc, data)
    idx = next_attempt_index(ATTEMPTS_DIR)
    write_attempt(idx, summary)
    print(f"Attempt {idx} recorded with rc={rc}")
    return rc


if __name__ == "__main__":
    raise SystemExit(main())

