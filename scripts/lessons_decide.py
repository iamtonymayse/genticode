#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Tuple, Dict


def load(p: Path) -> dict:
    return json.loads(Path(p).read_text() or "{}")


def summarize_classes(att: dict) -> set[str]:
    groups = att.get("groups", {}) or {}
    classes = set(groups.keys())
    return classes


def decide(prev: dict, curr: dict) -> Tuple[str, float]:
    prev_c = summarize_classes(prev)
    curr_c = summarize_classes(curr)
    new_classes = curr_c - prev_c
    base = len(prev_c) if prev_c else len(curr_c)
    pct = (len(new_classes) / max(1, base)) * 100.0
    decision = "RETRY" if pct > 50.0 else "SPLIT"
    return decision, pct


def main(argv=None) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--prev", required=True)
    ap.add_argument("--curr", required=True)
    args = ap.parse_args(argv)
    d, pct = decide(load(Path(args.prev)), load(Path(args.curr)))
    print(f"{d} ({pct:.1f}% new classes)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
