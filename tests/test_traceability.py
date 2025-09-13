from pathlib import Path
from genticode.traceability.parser import load_priority


def test_load_priority_ids(tmp_path):
    p = tmp_path / "PRIORITY.yaml"
    p.write_text("""
ids:
  - AC_0_1a
  - AC_0_2a
""")
    data = load_priority(p)
    assert data["ids"] == ["AC_0_1a", "AC_0_2a"]
