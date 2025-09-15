import importlib.util
from pathlib import Path
import json


def _load(repo_root: Path):
    mod_path = repo_root / "tools/intent_import.py"
    spec = importlib.util.spec_from_file_location("intent_import", mod_path)
    mod = importlib.util.module_from_spec(spec)
    assert spec and spec.loader
    spec.loader.exec_module(mod)  # type: ignore[attr-defined]
    return mod


def test_policy_patch_must_be_object(tmp_path):
    repo = Path(__file__).parents[1]
    mod = _load(repo)
    # Invalid POLICY payload (not a mapping)
    feed = [{"type": "POLICY", "data": 123}]
    try:
        mod.compute_changes(feed)
    except SystemExit as e:
        assert "POLICY patch must be an object" in str(e)
    else:
        raise AssertionError("expected SystemExit for invalid policy patch")


def test_cli_main_feed_not_found(tmp_path, capsys):
    repo = Path(__file__).parents[1]
    mod = _load(repo)
    code = mod.main([str(tmp_path / "no-such.jsonl"), "--dry-run"])  # explicit dry-run
    assert code == 2
    err = capsys.readouterr().err
    assert "Feed not found" in err


def test_cli_main_apply_prints_and_handles_docs_error(tmp_path, monkeypatch, capsys):
    repo = Path(__file__).parents[1]
    mod = _load(repo)
    # Redirect module paths to tmp
    mod.ROOT = tmp_path
    mod.SSOT_DIR = tmp_path / "ssot"
    mod.REQ_PATH = mod.SSOT_DIR / "requirements.yaml"
    mod.DEC_PATH = mod.SSOT_DIR / "decisions.yaml"
    mod.POLICY_PATH = mod.SSOT_DIR / "policy.yaml"
    # Prepare a minimal valid feed
    feed = tmp_path / "feed.jsonl"
    feed.write_text(json.dumps({
        "type": "REQ",
        "data": {"id": "REQ-Z", "title": "Z", "status": "ready", "acceptance": [{"id": "AC-Z", "text": "ok"}]}
    }) + "\n")

    # Monkeypatch docs_build to raise so apply_changes swallows exceptions
    import genticode.docsutil as docsutil
    monkeypatch.setattr(docsutil, "docs_build", lambda *_a, **_k: (_ for _ in ()).throw(RuntimeError("boom")))

    code = mod.main([str(feed), "--apply"])  # applies changes and prints message
    assert code == 0
    out = capsys.readouterr().out
    assert "Applied 1 change(s)." in out
    # Files were still written
    assert mod.REQ_PATH.exists()


def test_unknown_type_and_deep_merge_lists(tmp_path):
    repo = Path(__file__).parents[1]
    mod = _load(repo)
    # Unknown type
    try:
        mod.compute_changes([{ "type": "WHATEVER", "data": {} }])
    except SystemExit as e:
        assert "Unknown type" in str(e)
    else:
        raise AssertionError("expected SystemExit for unknown type")
    # Deep merge lists concatenates
    out = mod._deep_merge([1,2], [3])
    assert out == [1,2,3]
