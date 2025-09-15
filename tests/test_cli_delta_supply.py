import json
import subprocess, sys
from pathlib import Path
from shutil import copytree


def run(tmp: Path, *args: str) -> subprocess.CompletedProcess:
    return subprocess.run([sys.executable, "-m", "genticode", *args], cwd=tmp, capture_output=True, text=True)


def test_cli_computes_supply_delta_new_high(tmp_path: Path):
    copytree(Path(__file__).parents[1] / "genticode", tmp_path / "genticode")
    # First check -> no baseline
    assert run(tmp_path, "check").returncode in (0, 1, 2)
    # Capture baseline and run again to compute delta structure
    assert run(tmp_path, "baseline", "capture").returncode == 0
    assert run(tmp_path, "check").returncode in (0, 1, 2)
    data = json.loads((tmp_path / ".genticode/report.json").read_text())
    assert "delta" in data and "supply" in data["delta"] and "new_high" in data["delta"]["supply"]

