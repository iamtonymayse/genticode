from pathlib import Path
from genticode.docsutil import docs_build, gov_check


def _prep_base(tmp_path: Path):
    (tmp_path / "ssot").mkdir()
    (tmp_path / "ssot/requirements.yaml").write_text("items: []\n")
    (tmp_path / "ssot/decisions.yaml").write_text("items: []\n")
    (tmp_path / "PRD.md").write_text("# PRD\n")


def test_gov_policy_change_detected(tmp_path: Path):
    _prep_base(tmp_path)
    (tmp_path / ".genticode").mkdir()
    pol = tmp_path / ".genticode/policy.yaml"
    pol.write_text("version: 1\n")
    docs_build(tmp_path)
    # mutate policy to trigger change detection
    pol.write_text("version: 2\n")
    ok, msg = gov_check(tmp_path)
    assert not ok and "Policy change detected" in msg


def test_gov_schema_change_detected(tmp_path: Path):
    _prep_base(tmp_path)
    (tmp_path / ".genticode").mkdir()
    (tmp_path / ".genticode/policy.yaml").write_text("version: 1\n")
    sch = tmp_path / "schema"
    sch.mkdir()
    f = sch / "x.json"
    f.write_text("{}\n")
    docs_build(tmp_path)
    # mutate schema to trigger change detection
    f.write_text("{\n  \"k\": 1\n}\n")
    ok, msg = gov_check(tmp_path)
    assert not ok and "Schema change detected" in msg

