from __future__ import annotations

import os
import re
from dataclasses import dataclass
from pathlib import Path
from typing import Iterator, List
import os


SECRET_PATTERNS = [
    re.compile(r"aws_secret_access_key\b", re.I),
    re.compile(r"password\s*=\s*['\"]?\w+", re.I),
    re.compile(r"api[_-]?key\b", re.I),
    re.compile(r"\b\d{3}-\d{2}-\d{4}\b"),  # SSN-like
]


@dataclass(frozen=True)
class SecretFinding:
    file: Path
    line: int
    text: str


def scan_repo_for_secrets(root: Path) -> List[SecretFinding]:
    findings: List[SecretFinding] = []
    max_bytes = int(os.getenv("GENTICODE_MAX_FILE_BYTES", "1048576"))
    for dirpath, dirnames, filenames in os.walk(root):
        rel = os.path.relpath(dirpath, root)
        if rel.startswith(".git") or ".genticode" in rel or ".venv" in rel or "node_modules" in rel:
            continue
        for fn in filenames:
            p = Path(dirpath) / fn
            try:
                if p.stat().st_size > max_bytes:
                    continue
                src = p.read_text(encoding="utf-8", errors="ignore")
            except Exception:
                continue
            for i, line in enumerate(src.splitlines(), start=1):
                for pat in SECRET_PATTERNS:
                    if pat.search(line):
                        findings.append(SecretFinding(p, i, line.strip()))
                        break
    return findings
