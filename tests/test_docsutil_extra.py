from pathlib import Path
import subprocess, sys


def run_mod(tmp: Path, *args: str) -> int:
    cp = subprocess.run([sys.executable, "-m", "genticode", *args], cwd=tmp, capture_output=True, text=True)
    return cp.returncode


def test_gov_missing_snapshot(tmp_path):
    # create PRD without snapshot
    (tmp_path / "PRD.md").write_text("# PRD\n")
    (tmp_path / "ssot").mkdir()
    (tmp_path / "ssot/requirements.yaml").write_text("items: []\n")
    (tmp_path / "ssot/decisions.yaml").write_text("items: []\n")
    (tmp_path / ".genticode").mkdir()
    (tmp_path / ".genticode/policy.yaml").write_text("version: 1\n")
    rc = run_mod(tmp_path, "gov")
    assert rc != 0


def test_gov_parse_error(tmp_path):
    # invalid YAML in SSOT
    (tmp_path / "PRD.md").write_text("# PRD\n")
    (tmp_path / "ssot").mkdir()
    (tmp_path / "ssot/requirements.yaml").write_text("- not: valid: yaml: :\n")
    (tmp_path / "ssot/decisions.yaml").write_text("items: []\n")
    (tmp_path / ".genticode").mkdir()
    (tmp_path / ".genticode/policy.yaml").write_text("version: 1\n")
    rc = run_mod(tmp_path, "gov")
    assert rc != 0

