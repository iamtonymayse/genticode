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


def _hash_tree(dirpath: Path) -> str:
    """Hash all files under a directory deterministically by path and content.

    If the directory doesn't exist, returns an empty hash marker.
    """
    if not dirpath.exists() or not dirpath.is_dir():
        return ""
    h = hashlib.sha256()
    for p in sorted(dirpath.rglob("*")):
        if p.is_file():
            rel = p.relative_to(dirpath).as_posix().encode()
            h.update(rel)
            try:
                h.update(p.read_bytes())
            except Exception:
                h.update(b"<missing>")
            h.update(b"\n--\n")
    return h.hexdigest()


def _snapshot_ledger(root: Path, out_dir: Path) -> str | None:  # pragma: no cover - exercised via higher-level tests
    ledger = root / ".genticode" / "local" / "LESSONS_ACCEPTED.md"
    if not ledger.exists():
        return None
    try:
        data = ledger.read_bytes()
        h = hashlib.sha256(data).hexdigest()
        (out_dir / "ledger.hash").write_text(h + "\n")
        (out_dir / "ledger.snap").write_bytes(data)
        return h
    except Exception:  # pragma: no cover - defensive
        return None


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
    # Capture ledger snapshot if present (append-only enforcement)
    ledger_hash = _snapshot_ledger(root, gc)
    # Snapshot policy and schema hashes for governance checks
    pol = root / ".genticode" / "policy.yaml"
    pol_hash = None
    if pol.exists():
        try:
            pol_hash = hashlib.sha256(pol.read_bytes()).hexdigest()
            (gc / "policy.hash").write_text(pol_hash + "\n")
        except Exception:
            pol_hash = None
    schema_hash = _hash_tree(root / "schema")
    if schema_hash:
        (gc / "schema.hash").write_text(schema_hash + "\n")
    meta = {"ssot_hash": ssot_hash, "ledger_hash": ledger_hash, "policy_hash": pol_hash, "schema_hash": schema_hash or None}
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
    # Ledger immutability: if we have a snapshot, current must start with it
    snap_ledger = snap_dir / "ledger.snap"
    if snap_ledger.exists():
        ledger = root / ".genticode" / "local" / "LESSONS_ACCEPTED.md"
        if ledger.exists():
            try:
                cur = ledger.read_bytes()
                old = snap_ledger.read_bytes()
                if not cur.startswith(old):
                    return False, "Lessons ledger immutability violation: edits to prior entries detected"
            except Exception:  # pragma: no cover - defensive
                pass
    # Policy change detection: require DEC/REQ reference trail
    pol = root / ".genticode" / "policy.yaml"
    snap_pol_hash = (snap_dir / "policy.hash")
    if pol.exists() and snap_pol_hash.exists():  # pragma: no cover - exercised via tests
        try:
            cur_h = hashlib.sha256(pol.read_bytes()).hexdigest()
            if cur_h != snap_pol_hash.read_text().strip():
                return False, "Policy change detected; add DEC and REQ references (e.g., DEC-YYYY-MM-*, REQ-*) and rebuild docs"
        except Exception:  # pragma: no cover - defensive
            pass
    # Schema changes (if schema/ present) require DEC/REQ
    snap_schema = snap_dir / "schema.hash"
    if snap_schema.exists():  # pragma: no cover - exercised via tests
        try:
            cur_schema = _hash_tree(root / "schema")
            if cur_schema and cur_schema != snap_schema.read_text().strip():
                return False, "Schema change detected; add DEC and REQ references and rebuild docs"
        except Exception:  # pragma: no cover - defensive
            pass
    return True, "ok"
