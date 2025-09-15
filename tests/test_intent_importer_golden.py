import importlib.util
from pathlib import Path


def _load_importer(repo_root: Path):
    mod_path = repo_root / "tools/intent_import.py"
    spec = importlib.util.spec_from_file_location("intent_import", mod_path)
    mod = importlib.util.module_from_spec(spec)
    assert spec and spec.loader
    spec.loader.exec_module(mod)  # type: ignore[attr-defined]
    return mod


def test_importer_order_insensitive(tmp_path):
    repo = Path(__file__).parents[1]
    imp = _load_importer(repo)
    # Two feeds with reversed REQ order
    feed1 = tmp_path / "f1.jsonl"
    feed2 = tmp_path / "f2.jsonl"
    a = {"type": "REQ", "data": {"id": "REQ-A", "title": "A", "status": "ready", "acceptance": [{"id": "AC-A", "text": "a"}]}}
    b = {"type": "REQ", "data": {"id": "REQ-B", "title": "B", "status": "ready", "acceptance": [{"id": "AC-B", "text": "b"}]}}
    feed1.write_text("\n".join([imp.json.dumps(a), imp.json.dumps(b)]) + "\n")
    feed2.write_text("\n".join([imp.json.dumps(b), imp.json.dumps(a)]) + "\n")
    c1 = imp.compute_changes(imp._read_jsonl(feed1))
    c2 = imp.compute_changes(imp._read_jsonl(feed2))
    # Find requirements.yaml entries
    req_new1 = next(ch.new for ch in c1 if str(ch.path).endswith("requirements.yaml"))
    req_new2 = next(ch.new for ch in c2 if str(ch.path).endswith("requirements.yaml"))
    assert req_new1 == req_new2

