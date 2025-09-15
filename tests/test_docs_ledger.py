from pathlib import Path
import subprocess, sys, json, hashlib


def run_mod(tmp: Path, *args: str) -> subprocess.CompletedProcess:
    return subprocess.run([sys.executable, "-m", "genticode", *args], cwd=tmp, capture_output=True, text=True)


def test_ledger_append_only_enforced(tmp_path: Path):
    # Prepare minimal PRD and SSOT
    (tmp_path / "PRD.md").write_text("# PRD\n")
    (tmp_path / "ssot").mkdir()
    (tmp_path / "ssot/requirements.yaml").write_text("items: []\n")
    (tmp_path / "ssot/decisions.yaml").write_text("items: []\n")
    (tmp_path / ".genticode/local").mkdir(parents=True)
    ledger = tmp_path / ".genticode/local/LESSONS_ACCEPTED.md"
    ledger.write_text("A\nB\n")
    # Snapshot
    assert run_mod(tmp_path, "docs", "build").returncode == 0
    snap_dir = tmp_path / ".genticode/raw/docs_render"
    assert (snap_dir / "ledger.snap").exists()
    h_expected = hashlib.sha256("A\nB\n".encode()).hexdigest()
    assert (snap_dir / "ledger.hash").read_text().strip() == h_expected
    meta = json.loads((snap_dir / "meta.json").read_text())
    assert meta.get("ledger_hash") == h_expected
    # Append is allowed
    ledger.write_text("A\nB\nC\n")
    assert run_mod(tmp_path, "gov").returncode == 0
    # Editing prior entries should fail
    ledger.write_text("A\nX-EDIT\nC\n")
    assert run_mod(tmp_path, "gov").returncode != 0
