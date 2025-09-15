import importlib.util
from pathlib import Path
import json
import types


def _load(repo_root: Path):
    mod_path = repo_root / "tools/intent_import.py"
    spec = importlib.util.spec_from_file_location("intent_import", mod_path)
    mod = importlib.util.module_from_spec(spec)
    assert spec and spec.loader
    spec.loader.exec_module(mod)  # type: ignore[attr-defined]
    return mod


def test_read_jsonl_invalid_line(tmp_path):
    repo = Path(__file__).parents[1]
    mod = _load(repo)
    bad = tmp_path / "bad.jsonl"
    bad.write_text("{not json}\n")
    try:
        mod._read_jsonl(bad)
        assert False, "expected SystemExit"
    except SystemExit as e:
        assert "Invalid JSON" in str(e)


def test_compute_changes_dedupe_and_policy_merge(tmp_path):
    repo = Path(__file__).parents[1]
    mod = _load(repo)
    # Redirect module paths to tmp
    mod.ROOT = tmp_path
    mod.SSOT_DIR = tmp_path / "ssot"
    mod.REQ_PATH = mod.SSOT_DIR / "requirements.yaml"
    mod.DEC_PATH = mod.SSOT_DIR / "decisions.yaml"
    mod.POLICY_PATH = mod.SSOT_DIR / "policy.yaml"

    # Build feed with duplicate ACs and a policy patch
    feed = tmp_path / "feed.jsonl"
    feed.write_text("\n".join([
        json.dumps({
            "type": "REQ",
            "data": {
                "id": "REQ-X",
                "title": "X",
                "status": "ready",
                "acceptance": [
                    {"id": "AC-1", "text": "a"},
                    {"id": "AC-1", "text": "a-dup"}
                ]
            }
        }),
        json.dumps({
            "type": "DEC",
            "data": {"id": "DEC-2025-09-X", "context": "c", "decision": "d", "status": "draft"}
        }),
        json.dumps({
            "type": "POLICY",
            "data": {"budgets": {"static": {"high": 0}}}
        }),
    ]) + "\n")

    items = mod._read_jsonl(feed)
    changes = mod.compute_changes(items)
    # Compute out texts and ensure dedupe occurred
    req_change = next(c for c in changes if str(c.path).endswith("requirements.yaml"))
    data = json.loads(req_change.new)
    assert any(r["id"] == "REQ-X" for r in data)
    acs = next(r["acceptance"] for r in data if r["id"] == "REQ-X")
    assert len(acs) == 1 and acs[0]["id"] == "AC-1"
    pol_change = next(c for c in changes if str(c.path).endswith("policy.yaml"))
    pol = json.loads(pol_change.new)
    assert pol["budgets"]["static"]["high"] == 0


def test_apply_changes_writes_files_and_meta(tmp_path):
    repo = Path(__file__).parents[1]
    mod = _load(repo)
    # Redirect module paths to tmp
    mod.ROOT = tmp_path
    mod.SSOT_DIR = tmp_path / "ssot"
    mod.REQ_PATH = mod.SSOT_DIR / "requirements.yaml"
    mod.DEC_PATH = mod.SSOT_DIR / "decisions.yaml"
    mod.POLICY_PATH = mod.SSOT_DIR / "policy.yaml"

    items = [
        {"type": "REQ", "data": {"id": "REQ-Y", "title": "Y", "status": "ready", "acceptance": [{"id": "AC-Y", "text": "ok"}]}}
    ]
    changes = mod.compute_changes(items)
    mod.apply_changes(changes)
    assert mod.REQ_PATH.exists()
    # docs build creates changelog and meta under .genticode
    assert (tmp_path / "docs/changelog.md").exists()
    assert (tmp_path / ".genticode/raw/docs_render/meta.json").exists()


def test_loader_fallback_and_noop_changes(tmp_path):
    repo = Path(__file__).parents[1]
    mod = _load(repo)
    # Redirect module paths to tmp
    mod.ROOT = tmp_path
    mod.SSOT_DIR = tmp_path / "ssot"
    mod.REQ_PATH = mod.SSOT_DIR / "requirements.yaml"
    mod.DEC_PATH = mod.SSOT_DIR / "decisions.yaml"
    mod.POLICY_PATH = mod.SSOT_DIR / "policy.yaml"
    mod.SSOT_DIR.mkdir(parents=True, exist_ok=True)
    # Write non-JSON content to exercise fallback
    mod.REQ_PATH.write_text("items: []\n")
    mod.DEC_PATH.write_text("items: []\n")
    mod.POLICY_PATH.write_text("budgets: {}\n")
    # With empty feed, importer will normalize YAML-to-JSON text → yields 3 changes
    changes = mod.compute_changes([])
    paths = sorted([c.path.name for c in changes])
    assert paths == ["decisions.yaml", "policy.yaml", "requirements.yaml"]
