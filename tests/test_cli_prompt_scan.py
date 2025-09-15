import subprocess, sys
from pathlib import Path
from shutil import copytree


def run(tmp: Path, *args: str) -> subprocess.CompletedProcess:
    return subprocess.run([sys.executable, "-m", "genticode", *args], cwd=tmp, capture_output=True, text=True)


def test_cli_prompt_scan_writes_manifest(tmp_path: Path):
    copytree(Path(__file__).parents[1] / "genticode", tmp_path / "genticode")
    cp = run(tmp_path, "prompt", "scan", "--write-manifest")
    assert cp.returncode == 0
    assert (tmp_path / ".genticode/prompts.manifest.json").exists()
    assert (tmp_path / ".genticode/prompts.yaml").exists()

