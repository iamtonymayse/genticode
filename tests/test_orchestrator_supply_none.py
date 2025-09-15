from pathlib import Path

from genticode import orchestrator as orch


def test_supply_counts_when_sbom_tools_missing(tmp_path, monkeypatch):
    monkeypatch.setattr("genticode.orchestrator.maybe_cyclonedx_py", lambda root, out: None)
    monkeypatch.setattr("genticode.orchestrator.maybe_cyclonedx_npm", lambda root, out: None)
    counts = orch.run_supply_pack(tmp_path, tmp_path / ".genticode")
    assert counts["license_violations"] == 0
    assert counts["vulns"] == 0
    assert counts["components"]["python"] == 0 and counts["components"]["node"] == 0
    assert counts["sbom_present"] is False

