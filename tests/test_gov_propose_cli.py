import subprocess, sys
from pathlib import Path
from shutil import copytree
import json


def run_mod(tmp: Path, *args: str) -> subprocess.CompletedProcess:
    return subprocess.run([sys.executable, "-m", "genticode", *args], cwd=tmp, capture_output=True, text=True)


def test_gov_propose_emits_drafts(tmp_path: Path):
    # Work in isolated temp by copying package
    copytree(Path(__file__).parents[1] / "genticode", tmp_path / "genticode")
    # Run propose from lessons
    cp = run_mod(tmp_path, "gov", "propose", "--from", "lessons")
    assert cp.returncode == 0, cp.stderr
    req = json.loads((tmp_path / "ssot/requirements.yaml").read_text())
    dec = json.loads((tmp_path / "ssot/decisions.yaml").read_text())
    assert any(r.get("id") == "REQ-GOV-PROPOSE-01" for r in req)
    assert any(d.get("status") == "draft" for d in dec)
    # Second run should upsert, not duplicate
    cp2 = run_mod(tmp_path, "gov", "propose", "--from", "lessons")
    assert cp2.returncode == 0
    req2 = json.loads((tmp_path / "ssot/requirements.yaml").read_text())
    assert sum(1 for r in req2 if r.get("id") == "REQ-GOV-PROPOSE-01") == 1
