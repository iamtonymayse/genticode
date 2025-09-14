from __future__ import annotations

import json
from pathlib import Path
import re
from typing import Any


def _level_from_severity(sev: str) -> str:
    s = sev.lower()
    if s in ("critical", "high", "error"):
        return "error"
    if s in ("medium", "warning", "warn"):
        return "warning"
    return "note"


def _load_json(path: Path) -> Any:
    try:
        return json.loads(path.read_text())
    except Exception:
        return None


_SECRET_PATTERNS = [
    re.compile(r"\b(ghp_[A-Za-z0-9]{20,})\b"),
    re.compile(r"\b(github_pat_[A-Za-z0-9_]{20,})\b"),
    re.compile(r"\b(sk-[A-Za-z0-9]{20,})\b"),
    re.compile(r"\b(AKI[AD][0-9A-Z]{16})\b"),
]


def _redact(text: str) -> str:
    out = text
    for pat in _SECRET_PATTERNS:
        out = pat.sub("<REDACTED>", out)
    return out


def to_sarif(report: dict, gc_dir: Path | None = None) -> dict:
    """Build unified SARIF from available normalized artifacts.

    - Includes Prompt findings from `.genticode/prompts.manifest.json`
    - Includes Static findings from `.genticode/raw/semgrep.json` (if present)
    """
    gc = gc_dir or (Path.cwd() / ".genticode")
    results: list[dict] = []
    rules: dict[str, dict] = {}

    # Prompt manifest → SARIF
    pm = _load_json(gc / "prompts.manifest.json")
    if isinstance(pm, dict):
        for it in pm.get("items", []) or []:
            rid = "prompt.detected"
            rules.setdefault(rid, {"id": rid, "name": "Prompt detected"})
            message = _redact(f"Prompt-like string (role={it.get('role')})")
            loc = {
                "physicalLocation": {
                    "artifactLocation": {"uri": it.get("file")},
                    "region": {"startLine": int(it.get("start", 1))},
                }
            }
            results.append({
                "ruleId": rid,
                "level": "note",
                "message": {"text": message},
                "locations": [loc],
                "properties": {"id": it.get("id"), "role": it.get("role")},
            })
            # Add lint items as separate notes
            for code in it.get("lints", []) or []:
                lid = f"prompt.lint.{code.lower()}"
                rules.setdefault(lid, {"id": lid, "name": f"Prompt lint: {code}"})
                results.append({
                    "ruleId": lid,
                    "level": "warning",
                "message": {"text": _redact(code)},
                    "locations": [loc],
                    "properties": {"id": it.get("id")},
                })

    # Static (Semgrep JSON) → SARIF
    sg = _load_json(gc / "raw" / "semgrep.json")
    if isinstance(sg, dict):
        for r in sg.get("results", []) or []:
            rid = str(r.get("check_id") or r.get("extra", {}).get("check_id"))
            sev = (r.get("extra", {}).get("severity") or "info").lower()
            msg = _redact(r.get("extra", {}).get("message") or r.get("message") or rid)
            path = r.get("path") or r.get("extra", {}).get("path")
            start = (r.get("start", {}) or {}).get("line") or 1
            end = (r.get("end", {}) or {}).get("line") or start
            rules.setdefault(rid, {"id": rid, "name": rid})
            results.append({
                "ruleId": rid,
                "level": _level_from_severity(sev),
                "message": {"text": msg},
                "locations": [
                    {
                        "physicalLocation": {
                            "artifactLocation": {"uri": path},
                            "region": {"startLine": int(start), "endLine": int(end)},
                        }
                    }
                ],
            })

    return {
        "version": "2.1.0",
        "$schema": "https://json.schemastore.org/sarif-2.1.0.json",
        "runs": [
            {
                "tool": {
                    "driver": {
                        "name": "genticode",
                        "semanticVersion": str(report.get("genticode_version", "0")),
                        "rules": sorted(rules.values(), key=lambda d: d.get("id", "")),
                    }
                },
                "results": results,
            }
        ],
    }
