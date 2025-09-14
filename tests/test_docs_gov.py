from pathlib import Path
import subprocess, sys, json


def run_mod(tmp: Path, *args: str) -> int:
    cp = subprocess.run([sys.executable, "-m", "genticode", *args], cwd=tmp, capture_output=True, text=True)
    # print(cp.stdout, cp.stderr)
    return cp.returncode


def test_docs_build_and_gov_check(tmp_path):
    # minimal files
    (tmp_path / "PRD.md").write_text("# PRD\n")
    (tmp_path / "ADDH.md").write_text("# ADDH\n")
    (tmp_path / "ssot").mkdir()
    (tmp_path / "ssot/requirements.yaml").write_text("items: []\n")
    (tmp_path / "ssot/decisions.yaml").write_text("items: []\n")
    (tmp_path / ".genticode").mkdir()
    (tmp_path / ".genticode/policy.yaml").write_text("version: 1\n")
    # build
    assert run_mod(tmp_path, "docs", "build") == 0
    # gov check OK
    assert run_mod(tmp_path, "gov") == 0
    # drift: modify PRD.md directly
    (tmp_path / "PRD.md").write_text("# PRD drift\n")
    assert run_mod(tmp_path, "gov") != 0

