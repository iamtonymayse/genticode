from pathlib import Path
from genticode import orchestrator as orch
from genticode.policy import PolicyConfig, PackConfig


def test_static_secrets_count_included(tmp_path, monkeypatch):
    # copy fixture file
    src = Path(__file__).parent / "fixtures/static/secret.py"
    content = src.read_text()
    (tmp_path / "secret.py").write_text(content)
    counts = orch.run_static_pack(tmp_path, tmp_path / ".genticode")
    assert counts["secrets"] >= 1
    assert counts["by_severity"]["high"] >= counts["secrets"]


def test_static_ruleset_from_policy_passed(monkeypatch, tmp_path):
    captured = {}

    def fake_semgrep(root, out, timeout_s=120, configs=None):
        captured["configs"] = list(configs or [])
        return {"results": []}

    monkeypatch.setattr("genticode.orchestrator.maybe_run_semgrep", fake_semgrep)
    pol = PolicyConfig()
    pol.packs = {"static": PackConfig(enabled=True, ruleset=["r/python-security", "r/node-audit"]) }
    counts = orch.run_static_pack(tmp_path, tmp_path / ".genticode", pol)
    assert captured["configs"] == ["r/python-security", "r/node-audit"]
