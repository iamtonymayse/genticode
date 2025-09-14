#!/usr/bin/env python3
"""
Intent importer (MPI) for Water Spider

Reads a JSONL feed of items (types: REQ, DEC, POLICY, NOTE) and either
prints diffs (--dry-run, default) or applies changes (--apply) to SSOT
under ssot/ and triggers docs render.

Design goals (MPI):
- Minimal schema checks without external deps
- Deep-merge for POLICY patches
- Deterministic JSON-in-YAML output (YAML accepts JSON)
"""
from __future__ import annotations

import argparse
import difflib
import json
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Any


ROOT = Path.cwd()
SSOT_DIR = ROOT / "ssot"
REQ_PATH = SSOT_DIR / "requirements.yaml"
DEC_PATH = SSOT_DIR / "decisions.yaml"
POLICY_PATH = SSOT_DIR / "policy.yaml"


def _read_jsonl(path: Path) -> list[dict]:
    items: list[dict] = []
    for i, line in enumerate(path.read_text().splitlines(), 1):
        line = line.strip()
        if not line:
            continue
        try:
            obj = json.loads(line)
        except json.JSONDecodeError as e:
            raise SystemExit(f"Invalid JSON at line {i}: {e}")
        if not isinstance(obj, dict) or "type" not in obj:
            raise SystemExit(f"Invalid item at line {i}: expected object with 'type'")
        items.append(obj)
    return items


def _deep_merge(dst: Any, src: Any) -> Any:
    if isinstance(dst, dict) and isinstance(src, dict):
        out = dict(dst)
        for k, v in src.items():
            out[k] = _deep_merge(out.get(k), v) if k in out else v
        return out
    if isinstance(dst, list) and isinstance(src, list):
        return dst + src
    return src


def _validate_req(obj: dict) -> None:
    req = obj.get("data") if "data" in obj else obj
    missing = [k for k in ("id", "title", "status", "acceptance") if k not in req]
    if missing:
        raise SystemExit(f"REQ missing keys: {', '.join(missing)}")
    if not isinstance(req["acceptance"], list) or not req["acceptance"]:
        raise SystemExit("REQ.acceptance must be a non-empty list")
    for ac in req["acceptance"]:
        if not isinstance(ac, dict) or not {"id", "text"} <= set(ac):
            raise SystemExit("REQ.acceptance items must have id and text")


def _validate_dec(obj: dict) -> None:
    dec = obj.get("data") if "data" in obj else obj
    missing = [k for k in ("id", "context", "decision", "status") if k not in dec]
    if missing:
        raise SystemExit(f"DEC missing keys: {', '.join(missing)}")


def _load_json_yaml(path: Path, default: Any) -> Any:
    if not path.exists():
        return default
    txt = path.read_text().strip()
    if not txt:
        return default
    # YAML is a superset of JSON; for MPI we support JSON-formatted YAML
    try:
        return json.loads(txt)
    except json.JSONDecodeError:
        # Fallback: treat as opaque string, not structured
        return default


def _dump_json_yaml(data: Any) -> str:
    # Deterministic JSON dump to .yaml file
    return json.dumps(data, indent=2, sort_keys=True) + "\n"


@dataclass
class PendingChange:
    path: Path
    old: str
    new: str


def compute_changes(feed: list[dict]) -> list[PendingChange]:
    SSOT_DIR.mkdir(parents=True, exist_ok=True)
    reqs = _load_json_yaml(REQ_PATH, [])
    decs = _load_json_yaml(DEC_PATH, [])
    policy = _load_json_yaml(POLICY_PATH, {})

    # Index by id for merge/update
    req_by_id = {r.get("id"): r for r in (reqs or []) if isinstance(r, dict)}
    dec_by_id = {d.get("id"): d for d in (decs or []) if isinstance(d, dict)}

    for it in feed:
        t = it.get("type")
        if t == "NOTE":
            continue
        if t == "REQ":
            _validate_req(it)
            data = it.get("data") or {k: it[k] for k in ("id", "title", "status", "acceptance") if k in it}
            # Dedup ACs by id, keeping first occurrence
            seen = set()
            ac_new: list[dict] = []
            for ac in data.get("acceptance", []) or []:
                if ac.get("id") in seen:
                    continue
                seen.add(ac.get("id"))
                ac_new.append({"id": ac.get("id"), "text": ac.get("text"), "coverage": ac.get("coverage", "required")})
            data["acceptance"] = ac_new
            req_by_id[data["id"]] = data
        elif t == "DEC":
            _validate_dec(it)
            data = it.get("data") or {k: it[k] for k in ("id", "context", "decision", "status") if k in it}
            dec_by_id[data["id"]] = data
        elif t == "POLICY":
            patch = it.get("data") if "data" in it else (it.get("patch") or {})
            if not isinstance(patch, dict):
                raise SystemExit("POLICY patch must be an object")
            policy = _deep_merge(policy, patch)
        else:
            raise SystemExit(f"Unknown type: {t}")

    reqs_new = sorted(list(req_by_id.values()), key=lambda r: r.get("id", ""))
    decs_new = sorted(list(dec_by_id.values()), key=lambda d: d.get("id", ""))

    changes: list[PendingChange] = []
    for path, cur in (
        (REQ_PATH, _dump_json_yaml(reqs)),
        (DEC_PATH, _dump_json_yaml(decs)),
        (POLICY_PATH, _dump_json_yaml(policy)),
    ):
        new_txt = _dump_json_yaml({REQ_PATH: reqs_new, DEC_PATH: decs_new, POLICY_PATH: policy}[path])
        if cur != new_txt:
            changes.append(PendingChange(path=path, old=cur, new=new_txt))
    return changes


def print_diffs(changes: list[PendingChange]) -> None:
    for ch in changes:
        old_lines = ch.old.splitlines(keepends=True)
        new_lines = ch.new.splitlines(keepends=True)
        diff = difflib.unified_diff(
            old_lines,
            new_lines,
            fromfile=str(ch.path),
            tofile=str(ch.path),
        )
        sys.stdout.writelines(diff)


def apply_changes(changes: list[PendingChange]) -> None:
    for ch in changes:
        ch.path.parent.mkdir(parents=True, exist_ok=True)
        ch.path.write_text(ch.new)

    # Trigger docs build deterministically
    try:
        from genticode.docsutil import docs_build
        docs_build(ROOT)
    except Exception:
        pass


def main(argv: list[str] | None = None) -> int:
    p = argparse.ArgumentParser(description="Intent importer (MPI)")
    p.add_argument("feed", nargs="?", default=str(ROOT / "ssot/bootstrap/intent_feed.jsonl"))
    m = p.add_mutually_exclusive_group()
    m.add_argument("--dry-run", action="store_true", help="show diffs only (default)")
    m.add_argument("--apply", action="store_true", help="apply changes")
    args = p.parse_args(argv)

    path = Path(args.feed)
    if not path.exists():
        print(f"Feed not found: {path}", file=sys.stderr)
        return 2
    try:
        items = _read_jsonl(path)
        changes = compute_changes(items)
    except SystemExit as e:
        print(str(e), file=sys.stderr)
        return 2
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        return 2

    if args.apply:
        apply_changes(changes)
        print(f"Applied {len(changes)} change(s).")
        return 0
    # default dry-run
    print_diffs(changes)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

