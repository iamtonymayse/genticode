from __future__ import annotations

from pathlib import Path


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

