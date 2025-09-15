from pathlib import Path
import json

from genticode import orchestrator as orch


def test_supply_counts_with_both_sboms(tmp_path, monkeypatch):
    sample = json.loads((Path(__file__).parent / "fixtures/sbom/python.json").read_text())
    monkeypatch.setattr("genticode.orchestrator.maybe_cyclonedx_py", lambda root, out: sample)
    monkeypatch.setattr("genticode.orchestrator.maybe_cyclonedx_npm", lambda root, out: sample)
    counts = orch.run_supply_pack(tmp_path, tmp_path / ".genticode")
    # One denied per SBOM -> 2 total
    assert counts["license_violations"] == 2
    assert counts["components"]["python"] > 0 and counts["components"]["node"] > 0

