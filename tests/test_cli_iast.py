import subprocess, sys
from pathlib import Path
from shutil import copytree


def run(tmp: Path, *args: str) -> subprocess.CompletedProcess:
    return subprocess.run([sys.executable, "-m", "genticode", *args], cwd=tmp, capture_output=True, text=True)


def test_cli_iast_null_provider(tmp_path: Path):
    copytree(Path(__file__).parents[1] / "genticode", tmp_path / "genticode")
    cp = run(tmp_path, "iast")
    assert cp.returncode == 0
    assert "IAST null provider" in (cp.stdout + cp.stderr)

