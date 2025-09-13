from pathlib import Path
from genticode.static.secrets import scan_repo_for_secrets


def test_scan_repo_for_secrets_finds_patterns(tmp_path):
    (tmp_path / "a.py").write_text("aws_secret_access_key='xyz'\n")
    (tmp_path / "b.txt").write_text("password = 'secret'\n")
    findings = scan_repo_for_secrets(tmp_path)
    texts = [f.text for f in findings]
    assert any('aws_secret_access_key' in t for t in texts)
    assert any('password' in t for t in texts)

