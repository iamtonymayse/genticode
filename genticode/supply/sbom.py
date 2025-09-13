from __future__ import annotations

import json
import shutil
import subprocess
from pathlib import Path


def maybe_cyclonedx_py(root: Path, out: Path) -> dict | None:
    if shutil.which("cyclonedx-py") is None:
        return None
    try:
        cp = subprocess.run(["cyclonedx-py", "-o", str(out)], cwd=str(root), capture_output=True, text=True, check=False)
        # Tool may write directly to file; try to read it
        if out.exists():
            return json.loads(out.read_text() or "{}")
        return json.loads(cp.stdout or "{}")
    except Exception:
        return None


def maybe_cyclonedx_npm(root: Path, out: Path) -> dict | None:
    if shutil.which("npx") is None:
        return None
    try:
        cp = subprocess.run([
            "npx",
            "@cyclonedx/cyclonedx-npm",
            "--output-format",
            "json",
            "--output-file",
            str(out),
        ], cwd=str(root), capture_output=True, text=True, check=False)
        if out.exists():
            return json.loads(out.read_text() or "{}")
        return json.loads(cp.stdout or "{}")
    except Exception:
        return None

