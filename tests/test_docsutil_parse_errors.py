from pathlib import Path
from genticode.docsutil import gov_check


def test_gov_check_yaml_parse_error(tmp_path: Path):
    # Write malformed YAML in SSOT files
    (tmp_path / "ssot").mkdir()
    (tmp_path / "ssot/requirements.yaml").write_text("items: [1,\n")
    (tmp_path / "ssot/decisions.yaml").write_text("items: []\n")
    ok, msg = gov_check(tmp_path)
    assert not ok and "SSOT parse error" in msg

