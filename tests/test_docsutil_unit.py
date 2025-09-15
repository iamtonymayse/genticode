from pathlib import Path
from genticode.docsutil import docs_build, gov_check, _hash_files
import json


def test_docs_build_and_gov_ok(tmp_path: Path):
    (tmp_path / "PRD.md").write_text("# PRD\n")
    (tmp_path / "ADDH.md").write_text("# ADDH\n")
    (tmp_path / "ssot").mkdir()
    (tmp_path / "ssot/requirements.yaml").write_text("items: []\n")
    (tmp_path / "ssot/decisions.yaml").write_text("items: []\n")
    (tmp_path / ".genticode").mkdir()
    (tmp_path / ".genticode/policy.yaml").write_text("version: 1\n")
    out = docs_build(tmp_path)
    assert (out / "PRD.md").exists()
    assert (out / "ADDH.md").exists()
    ok, msg = gov_check(tmp_path)
    assert ok and msg == "ok"


def test_gov_drift_detected(tmp_path: Path):
    (tmp_path / "PRD.md").write_text("# PRD\n")
    (tmp_path / "ADDH.md").write_text("# ADDH\n")
    (tmp_path / "ssot").mkdir()
    (tmp_path / "ssot/requirements.yaml").write_text("items: []\n")
    (tmp_path / "ssot/decisions.yaml").write_text("items: []\n")
    (tmp_path / ".genticode").mkdir()
    (tmp_path / ".genticode/policy.yaml").write_text("version: 1\n")
    docs_build(tmp_path)
    # mutate PRD after snapshot
    (tmp_path / "PRD.md").write_text("# PRD changed\n")
    ok, msg = gov_check(tmp_path)
    assert not ok and "drift" in msg


def test_hash_files_handles_missing_and_dirs(tmp_path: Path):
    # Include a directory to trigger exception path
    h = _hash_files([tmp_path])
    assert isinstance(h, str) and len(h) == 64
    # And a regular file to cover success path
    f = tmp_path / "f.txt"
    f.write_text("x")
    h2 = _hash_files([f])
    assert isinstance(h2, str) and len(h2) == 64 and h2 != ""


def test_docs_build_without_prd_addh(tmp_path: Path):
    # No PRD/ADDH present; ensure docs_build still writes meta.json
    (tmp_path / "ssot").mkdir()
    (tmp_path / "ssot/requirements.yaml").write_text("items: []\n")
    (tmp_path / "ssot/decisions.yaml").write_text("items: []\n")
    out = docs_build(tmp_path)
    assert (out / "meta.json").exists()
    meta = json.loads((out / "meta.json").read_text())
    assert meta.get("ledger_hash") is None


def test_docs_build_snapshots_policy_and_schema(tmp_path: Path):
    # Prepare policy and schema and ensure snapshots are written and gov passes when unchanged
    (tmp_path / ".genticode").mkdir()
    (tmp_path / ".genticode/policy.yaml").write_text("version: 1\n")
    (tmp_path / "schema").mkdir()
    (tmp_path / "schema/x.json").write_text("{}\n")
    (tmp_path / "ssot").mkdir()
    (tmp_path / "ssot/requirements.yaml").write_text("items: []\n")
    (tmp_path / "ssot/decisions.yaml").write_text("items: []\n")
    (tmp_path / "PRD.md").write_text("# PRD\n")
    out = docs_build(tmp_path)
    assert (out / "policy.hash").exists()
    assert (out / "schema.hash").exists()
    ok, _ = gov_check(tmp_path)
    assert ok


def test_gov_check_ledger_without_snapshot(tmp_path: Path):
    # No PRD snapshot present and no PRD file; ledger snapshot missing should not fail
    (tmp_path / "ssot").mkdir()
    (tmp_path / "ssot/requirements.yaml").write_text("items: []\n")
    (tmp_path / "ssot/decisions.yaml").write_text("items: []\n")
    (tmp_path / ".genticode/local").mkdir(parents=True)
    (tmp_path / ".genticode/local/LESSONS_ACCEPTED.md").write_text("only-current\n")
    # No snapshot created; gov should not enforce ledger and pass
    ok, msg = gov_check(tmp_path)
    assert ok
