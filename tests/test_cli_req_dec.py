import subprocess, sys
from pathlib import Path
from shutil import copytree


def run_mod(tmp: Path, *args: str) -> subprocess.CompletedProcess:
    return subprocess.run([sys.executable, "-m", "genticode", *args], cwd=tmp, capture_output=True, text=True)


def test_req_dec_cli_flow(tmp_path: Path):
    # copy package to temp so we don't touch repo SSOT
    from pathlib import Path as _P
    root = _P(__file__).parents[1]
    copytree(root / "genticode", tmp_path / "genticode")
    # create REQ with >=1 AC
    cp = run_mod(tmp_path, "req", "new", "--id", "REQ-TEST-1", "--title", "T", "--status", "ready", "--ac", "AC-1:ok")
    assert cp.returncode == 0, cp.stderr
    assert (tmp_path / "ssot/requirements.yaml").exists()
    # DEC with id pattern
    cp2 = run_mod(tmp_path, "dec", "new", "--id", "DEC-2025-09-Thing", "--context", "c", "--decision", "d")
    assert cp2.returncode == 0, cp2.stderr
    assert (tmp_path / "ssot/decisions.yaml").exists()
    # invalid REQ id should fail
    bad = run_mod(tmp_path, "req", "new", "--id", "BAD", "--title", "T", "--ac", "AC-1:x")
    assert bad.returncode != 0

