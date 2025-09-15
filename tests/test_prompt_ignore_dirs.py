from pathlib import Path
from genticode.prompt.detect import scan_repo


def test_scan_repo_ignores_generated_dirs(tmp_path):
    # Create a prompt-like file under images/ and ssot/
    (tmp_path / "images").mkdir()
    (tmp_path / "images/p.py").write_text("""You are a bot\n""")
    (tmp_path / "ssot").mkdir()
    (tmp_path / "ssot/p.py").write_text("""system: do not scan\n""")
    # And a valid source file under src/ (may or may not be detected depending on heuristics)
    (tmp_path / "src").mkdir()
    (tmp_path / "src/s.py").write_text("""You are a helper\n""")
    spans = scan_repo(tmp_path)
    files = {s.file.name for s in spans}
    # Generated dirs should be ignored: no p.py entries from images/ or ssot/
    assert "p.py" not in files
