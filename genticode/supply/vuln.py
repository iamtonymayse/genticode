from __future__ import annotations

import json
import shutil
import subprocess
from pathlib import Path
from typing import Any, Iterable


def maybe_pip_audit(root: Path, out: Path) -> dict | None:
    if shutil.which("pip-audit") is None:
        return None
    try:
        cp = subprocess.run([
            "pip-audit", "-f", "json"
        ], cwd=str(root), capture_output=True, text=True, check=False)
        data = json.loads(cp.stdout or "{}")
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_text(json.dumps(data, indent=2, sort_keys=True) + "\n")
        return data
    except Exception:
        return None


def maybe_npm_audit(root: Path, out: Path) -> dict | None:
    # Prefer npm audit for availability
    if shutil.which("npm") is None:
        return None
    try:
        cp = subprocess.run([
            "npm", "audit", "--json"
        ], cwd=str(root), capture_output=True, text=True, check=False)
        data = json.loads(cp.stdout or "{}")
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_text(json.dumps(data, indent=2, sort_keys=True) + "\n")
        return data
    except Exception:
        return None


def normalize_pip_audit(data: dict) -> list[dict[str, Any]]:
    vulns: list[dict[str, Any]] = []
    for v in data.get("vulns", []) or []:
        sev = (v.get("severity") or "info").lower()
        pkg = v.get("name") or v.get("package", {}).get("name")
        vulns.append({"tool": "pip-audit", "package": pkg, "severity": sev})
    return vulns


def normalize_npm_audit(data: dict) -> list[dict[str, Any]]:
    vulns: list[dict[str, Any]] = []
    advisories = data.get("advisories")
    if isinstance(advisories, dict):
        # npm <7 style
        for adv in advisories.values():
            sev = (adv.get("severity") or "info").lower()
            module = adv.get("module_name")
            vulns.append({"tool": "npm-audit", "package": module, "severity": sev})
    else:
        # npm >=7 uses vulnerabilities map; approximate
        vulns_map = data.get("vulnerabilities") or {}
        if isinstance(vulns_map, dict):
            for name, meta in vulns_map.items():
                sev = (meta.get("severity") or "info").lower()
                vulns.append({"tool": "npm-audit", "package": name, "severity": sev})
    return vulns
