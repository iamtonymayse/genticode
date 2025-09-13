from pathlib import Path
import json
from genticode.report import write_json


def test_write_json_roundtrip(tmp_path):
    out = tmp_path / "out.json"
    data = {"a": 1, "b": [2, 3]}
    write_json(out, data)
    loaded = json.loads(out.read_text())
    assert loaded == data

