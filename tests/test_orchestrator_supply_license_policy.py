from pathlib import Path

from genticode import orchestrator as orch


def test_supply_license_policy_fail_on_unknown_false(tmp_path, monkeypatch):
    # SBOM with unknown license only
    sbom = {"components": [{"licenses": [{"license": {"id": "FooBar-1.0"}}]}]}
    monkeypatch.setattr("genticode.orchestrator.maybe_cyclonedx_py", lambda root, out: sbom)
    monkeypatch.setattr("genticode.orchestrator.maybe_cyclonedx_npm", lambda root, out: None)
    class P:
        licenses = {"allow": [], "deny": [], "fail_on_unknown": False}
    counts = orch.run_supply_pack(tmp_path, tmp_path / ".genticode", policy=P())
    # No violations when unknowns are allowed
    assert counts["license_violations"] == 0


def test_supply_license_policy_deny_specific(tmp_path, monkeypatch):
    # SBOM with MIT only; deny MIT => 1 violation
    sbom = {"components": [{"licenses": [{"license": {"id": "MIT"}}]}]}
    monkeypatch.setattr("genticode.orchestrator.maybe_cyclonedx_py", lambda root, out: sbom)
    monkeypatch.setattr("genticode.orchestrator.maybe_cyclonedx_npm", lambda root, out: None)
    class P:
        licenses = {"allow": [], "deny": ["MIT"], "fail_on_unknown": True}
    counts = orch.run_supply_pack(tmp_path, tmp_path / ".genticode", policy=P())
    assert counts["license_violations"] == 1
