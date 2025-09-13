import json
import os
import shutil
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
GC = ROOT / ".genticode"


import sys


def run(*args: str) -> subprocess.CompletedProcess:
    return subprocess.run(
        [sys.executable, "-m", "genticode", *args],
        cwd=str(ROOT),
        capture_output=True,
        text=True,
        check=True,
    )


def setup_module(module):  # noqa: D401
    # Clean artifacts between test runs for determinism
    if GC.exists():
        shutil.rmtree(GC)


def test_init_creates_files(tmp_path):
    cp = run("init")
    assert (GC / "policy.yaml").exists(), cp.stdout
    assert (ROOT / "PRIORITY.yaml").exists(), cp.stdout


def test_check_produces_report():
    run("init")
    cp = run("check")
    out = GC / "report.json"
    assert out.exists(), cp.stdout
    data = json.loads(out.read_text())
    assert data["schema_version"] == "0.1.0"
    assert data["summary"]["counts"]["total"] == 0


def test_report_html_and_sarif_outputs():
    run("init")
    run("check")
    # Explicit flags
    run("report", "--html")
    run("report", "--sarif")
    assert (GC / "report.html").exists()
    assert (GC / "sarif.json").exists()
    # No flags => both
    (GC / "report.html").unlink()
    (GC / "sarif.json").unlink()
    run("report")
    assert (GC / "report.html").exists()
    assert (GC / "sarif.json").exists()


def test_baseline_capture_and_clear():
    run("init")
    run("check")
    cp = run("baseline", "capture")
    assert (GC / "baseline" / "report.json").exists(), cp.stdout
    # check again with baseline present
    run("check")
    data = json.loads((GC / "report.json").read_text())
    assert data["baseline"]["present"] is True
    # clear
    run("baseline", "clear")
    assert (GC / "baseline").exists() and not any((GC / "baseline").glob("*.json"))
