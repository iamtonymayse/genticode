import json
from pathlib import Path

from genticode.supply.vuln import maybe_pip_audit, maybe_npm_audit, normalize_pip_audit, normalize_npm_audit
from genticode import orchestrator as orch


def test_maybe_pip_audit_and_normalize(monkeypatch, tmp_path):
    sample = (Path(__file__).parent / "fixtures/vuln/pip_audit.json").read_text()

    class FakeCP:
        def __init__(self, stdout: str):
            self.stdout = stdout

    monkeypatch.setattr("shutil.which", lambda _: "/usr/bin/pip-audit")
    monkeypatch.setattr("subprocess.run", lambda *a, **k: FakeCP(stdout=sample))
    data = maybe_pip_audit(tmp_path, tmp_path / ".genticode/raw/pip-audit.json")
    assert data is not None
    vulns = normalize_pip_audit(data)
    assert len(vulns) == 2 and {v["severity"] for v in vulns} == {"high", "medium"}


def test_orchestrator_supply_vulns_aggregated(monkeypatch, tmp_path):
    # make pip-audit return sample; npm audit returns empty
    pa = json.loads((Path(__file__).parent / "fixtures/vuln/pip_audit.json").read_text())
    class FakeCP:
        def __init__(self, stdout: str):
            self.stdout = stdout
    monkeypatch.setattr("genticode.orchestrator.maybe_pip_audit", lambda root, out: pa)
    monkeypatch.setattr("genticode.orchestrator.normalize_pip_audit", lambda d: [{"severity": "high"}, {"severity": "medium"}])
    monkeypatch.setattr("genticode.orchestrator.maybe_npm_audit", lambda root, out: None)
    counts = orch.run_supply_pack(tmp_path, tmp_path / ".genticode")
    assert counts["vulns"] == 2 and counts["by_severity"]["high"] == 1
    assert "license_violations" in counts


def test_normalize_npm_audit_variants():
    from genticode.supply.vuln import normalize_npm_audit
    # npm <7 advisories dict
    legacy = {"advisories": {"1": {"severity": "low", "module_name": "leftpad"}}}
    out1 = normalize_npm_audit(legacy)
    assert out1 and out1[0]["package"] == "leftpad" and out1[0]["severity"] == "low"
    # npm >=7 vulnerabilities map
    modern = {"vulnerabilities": {"minimist": {"severity": "high"}}}
    out2 = normalize_npm_audit(modern)
    assert out2 and out2[0]["package"] == "minimist" and out2[0]["severity"] == "high"


def test_maybe_npm_audit_and_normalize(monkeypatch, tmp_path):
    sample = json.dumps({"vulnerabilities": {"minimist": {"severity": "high"}}})
    class FakeCP:
        def __init__(self, stdout: str):
            self.stdout = stdout
    monkeypatch.setattr("shutil.which", lambda name: "/usr/bin/npm" if name == "npm" else "/usr/bin/pip-audit")
    monkeypatch.setattr("subprocess.run", lambda *a, **k: FakeCP(stdout=sample))
    data = maybe_npm_audit(tmp_path, tmp_path / ".genticode/raw/npm-audit.json")
    assert data is not None
    out = normalize_npm_audit(data)
    assert out and out[0]["severity"] == "high"


def test_vuln_tools_missing(monkeypatch, tmp_path):
    monkeypatch.setattr("shutil.which", lambda name: None)
    assert maybe_pip_audit(tmp_path, tmp_path / "x.json") is None
    assert maybe_npm_audit(tmp_path, tmp_path / "y.json") is None
