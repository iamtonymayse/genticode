from pathlib import Path
from genticode.docsutil import _hash_tree


def test_hash_tree_nonempty_and_changes(tmp_path: Path):
    d = tmp_path / "schema"
    (d / "a").mkdir(parents=True)
    f = d / "a/x.json"
    f.write_text("{}\n")
    h1 = _hash_tree(d)
    assert isinstance(h1, str) and len(h1) == 64
    # change content → hash changes
    f.write_text("{\n \"k\": 1}\n")
    h2 = _hash_tree(d)
    assert h1 != h2
    # empty dir returns empty string
    assert _hash_tree(tmp_path / "empty") == ""

