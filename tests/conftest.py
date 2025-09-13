from __future__ import annotations

import sys
from pathlib import Path


# Ensure repo root is importable for package imports in tests
ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

