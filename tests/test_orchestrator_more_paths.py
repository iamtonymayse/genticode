from pathlib import Path

from genticode.orchestrator import run_static_pack, run_supply_pack
from genticode.policy import PolicyConfig


def test_static_ruleset_passed_to_semgrep(tmp_path, monkeypatch):
    # Arrange policy with ruleset and capture configs argument
    pol = PolicyConfig()
    pol.packs = {"static": type("X", (), {"enabled": True, "timeout_s": 10, "ruleset": "p/python"})()}

    captured = {}
    def fake_semgrep(root, out, configs=None):
        captured["configs"] = configs
        return None

    monkeypatch.setattr("genticode.orchestrator.maybe_run_semgrep", fake_semgrep)
    counts = run_static_pack(tmp_path, tmp_path / ".genticode", policy=pol)
    assert counts["findings"] == 0
    assert captured.get("configs") == ["p/python"]


def test_supply_lockfile_only_filters_sboms(tmp_path, monkeypatch):
    pol = PolicyConfig()
    pol.licenses = {"lockfile_only": True}
    # Make adapters return non-empty SBOMs, but without lockfiles they should be ignored
    dummy = {"components": [{"licenses": []}]}
    monkeypatch.setattr("genticode.orchestrator.maybe_cyclonedx_py", lambda root, out: dummy)
    monkeypatch.setattr("genticode.orchestrator.maybe_cyclonedx_npm", lambda root, out: dummy)
    counts = run_supply_pack(tmp_path, tmp_path / ".genticode", policy=pol)
    assert counts["sbom_present"] is False
    assert counts["components"] == {"python": 0, "node": 0}

