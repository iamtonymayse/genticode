from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Iterable


def _hash_files(paths: Iterable[Path]) -> str:
    h = hashlib.sha256()
    for p in sorted(paths, key=lambda x: str(x)):
        try:
            h.update(p.read_bytes())
        except Exception:
            h.update(b"<missing>")
        h.update(b"\n--\n")
    return h.hexdigest()


def docs_build(root: Path) -> Path:
    """Snapshot docs deterministically under `.genticode/raw/docs_render/`.

    Writes PRD.md and ADDH.md snapshots and a meta.json with ssot hash.
    """
    gc = root / ".genticode" / "raw" / "docs_render"
    gc.mkdir(parents=True, exist_ok=True)
    prd = root / "PRD.md"
    addh = root / "ADDH.md"
    # Compute SSOT hash
    ssot_files = [
        root / "ssot" / "requirements.yaml",
        root / "ssot" / "decisions.yaml",
        root / ".genticode" / "policy.yaml",
    ]
    ssot_hash = _hash_files(ssot_files)
    # Copy files deterministically (line endings preserved)
    if prd.exists():
        (gc / "PRD.md").write_bytes(prd.read_bytes())
    if addh.exists():
        (gc / "ADDH.md").write_bytes(addh.read_bytes())
    # Minimal changelog derived from hash
    (root / "docs").mkdir(exist_ok=True)
    (root / "docs" / "changelog.md").write_text(f"SSOT hash: {ssot_hash}\n")
    meta = {"ssot_hash": ssot_hash}
    (gc / "meta.json").write_text(json.dumps(meta, indent=2, sort_keys=True) + "\n")
    return gc


def gov_check(root: Path) -> tuple[bool, str]:
    """Validate SSOT YAML parse and doc drift.

    Returns (ok, message). Drift means PRD.md differs from last snapshot.
    """
    import yaml  # type: ignore

    # Parse SSOT YAMLs
    for name in ("requirements.yaml", "decisions.yaml"):
        p = root / "ssot" / name
        try:
            yaml.safe_load(p.read_text())
        except Exception as e:
            return False, f"SSOT parse error in {p}: {e}"

    # Drift check
    snap_dir = root / ".genticode" / "raw" / "docs_render"
    prd = root / "PRD.md"
    snap_prd = snap_dir / "PRD.md"
    if prd.exists():
        if not snap_prd.exists():
            return False, "No PRD snapshot found — run 'genticode docs build'"
        if prd.read_bytes() != snap_prd.read_bytes():
            return False, "PRD.md drift detected; edits must come from 'genticode docs build'"
    return True, "ok"

