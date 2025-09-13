from __future__ import annotations

from pathlib import Path
import os


def load_priority(path: Path) -> dict:
    """Very small PRIORITY.yaml reader expecting minimal structure:
    ids:
      - AC_0_1a
      - AC_0_2a
    """
    if not path.exists():
        return {"ids": []}
    ids: list[str] = []
    for line in path.read_text().splitlines():
        line = line.strip()
        if line.startswith("- "):
            ids.append(line[2:].strip())
    return {"ids": ids}


def scan_test_coverage(root: Path, ids: list[str]) -> dict:
    """Scan test files for occurrences of AC IDs.

    Simple heuristic: look for ID substrings in files under `tests/`.
    Returns {id: count} for matches found.
    """
    coverage: dict[str, int] = {i: 0 for i in ids}
    test_root = root / "tests"
    if not test_root.exists():
        return coverage
    for dirpath, dirnames, filenames in os.walk(test_root):
        for fn in filenames:
            p = Path(dirpath) / fn
            try:
                s = p.read_text(encoding="utf-8", errors="ignore")
            except Exception:
                continue
            for i in ids:
                if i in s:
                    coverage[i] += 1
    return coverage
