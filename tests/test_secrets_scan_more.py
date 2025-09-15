from pathlib import Path
from genticode.static.secrets import scan_repo_for_secrets


def test_scan_repo_for_secrets_more_patterns_and_ignores(tmp_path: Path):
    # Ignored dirs
    (tmp_path / ".git").mkdir()
    (tmp_path / ".git/secret.txt").write_text("password=oops\n")
    # Valid files
    (tmp_path / "c.js").write_text("const api_key = 'k';\n")
    (tmp_path / "d.txt").write_text("123-45-6789\n")
    findings = scan_repo_for_secrets(tmp_path)
    texts = [f.text for f in findings]
    assert any('api_key' in t for t in texts)
    assert any('123-45-6789' in t for t in texts)
    # ensure .git file ignored
    assert not any('oops' in t for t in texts)

