from pathlib import Path

from genticode import orchestrator as orch


def test_static_secrets_increment_high_severity(tmp_path, monkeypatch):
    # Create a small file with a secret-like pattern
    (tmp_path / "a.py").write_text("password = 'secret'\n")
    # Disable semgrep path to isolate secrets path
    monkeypatch.setattr("genticode.orchestrator.maybe_run_semgrep", lambda root, out, **kw: None)
    counts = orch.run_static_pack(tmp_path, tmp_path / ".genticode")
    assert counts["secrets"] >= 1
    assert counts["by_severity"]["high"] >= 1

