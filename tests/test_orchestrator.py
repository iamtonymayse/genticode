from pathlib import Path

from genticode.orchestrator import run_all, PackRunner
from genticode.policy import PolicyConfig, PackConfig
from genticode import orchestrator as orch


def test_orchestrator_respects_pack_enabled(tmp_path, monkeypatch):
    # Prepare fake runners that don't touch the filesystem
    def ok_runner(root: Path, gc: Path):
        return {"x": 1}

    packs = {
        "prompt": PackRunner("prompt", ok_runner),
        "static": PackRunner("static", ok_runner),
    }
    # Disable static via policy
    pol = PolicyConfig()
    pol.packs = {"prompt": PackConfig(enabled=True), "static": PackConfig(enabled=False)}
    report = {"packs": []}
    run_all(pol, tmp_path, tmp_path / ".genticode", report, packs=packs)
    names = [p["name"] for p in report["packs"]]
    assert "prompt" in names and "static" not in names


def test_orchestrator_continues_on_pack_error(tmp_path, monkeypatch):
    def ok_runner(root: Path, gc: Path):
        return {"x": 1}

    def bad_runner(root: Path, gc: Path):
        raise RuntimeError("boom")

    packs = {
        "prompt": PackRunner("prompt", ok_runner),
        "static": PackRunner("static", bad_runner),
        "quality": PackRunner("quality", ok_runner),
    }
    pol = PolicyConfig()
    report = {"packs": []}
    run_all(pol, tmp_path, tmp_path / ".genticode", report, packs=packs)
    summary = {p["name"]: p for p in report["packs"]}
    assert "prompt" in summary and "quality" in summary and "static" in summary
    assert summary["static"]["counts"].get("error")


def test_pack_helper_quality_and_traceability(tmp_path, monkeypatch):
    # quality passthrough
    monkeypatch.setattr("genticode.orchestrator.maybe_run_quality", lambda root: {"findings": 7})
    qc = orch.run_quality_pack(tmp_path, tmp_path / ".genticode")
    assert qc == {"findings": 7}

    # traceability reads PRIORITY.yaml
    (tmp_path / "PRIORITY.yaml").write_text("ids:\n  - AC_1\n  - AC_2\n")
    tc = orch.run_traceability_pack(tmp_path, tmp_path / ".genticode")
    assert tc["ac_ids"] == 2 and tc["uncovered"] == 2 and tc["covered"] == 0


def test_pack_helper_prompt_writes_artifacts(tmp_path, monkeypatch):
    # Simulate a single prompt span via manifest builder
    monkeypatch.setattr("genticode.orchestrator.prompt_scan", lambda root: [])
    monkeypatch.setattr("genticode.orchestrator.build_manifest", lambda spans: {"items": [{"file": "f.py", "start": 1, "end": 1}]})
    counts = orch.run_prompt_pack(tmp_path, tmp_path / ".genticode")
    assert counts["prompts"] == 1
    assert (tmp_path / ".genticode/prompts.manifest.json").exists()
    assert (tmp_path / ".genticode/raw/spans.json").exists()


def test_pack_helper_static_counts(tmp_path, monkeypatch):
    # No semgrep available → zero counts
    monkeypatch.setattr("genticode.orchestrator.maybe_run_semgrep", lambda root, out, **kw: None)
    sc = orch.run_static_pack(tmp_path, tmp_path / ".genticode")
    assert sc["findings"] == 0
    # With results
    sample = {
        "results": [
            {"check_id": "r1", "extra": {"severity": "HIGH"}},
            {"check_id": "r2", "extra": {"severity": "MEDIUM"}},
            {"check_id": "r3", "extra": {"severity": "HIGH"}},
        ]
    }
    monkeypatch.setattr("genticode.orchestrator.maybe_run_semgrep", lambda root, out, **kw: sample)
    monkeypatch.setattr("genticode.orchestrator.normalize_semgrep", lambda data: [
        {"severity": "high"}, {"severity": "medium"}, {"severity": "high"}
    ])
    sc2 = orch.run_static_pack(tmp_path, tmp_path / ".genticode")
    assert sc2["findings"] == 3 and sc2["by_severity"]["high"] == 2


def test_pack_helper_supply_counts(tmp_path, monkeypatch):
    # Both SBOM adapters return data to exercise license evaluator
    sbom = {"components": [
        {"licenses": [{"license": {"id": "MIT"}}]},
        {"licenses": [{"license": {"id": "AGPL-3.0"}}]}
    ]}
    monkeypatch.setattr("genticode.orchestrator.maybe_cyclonedx_py", lambda root, out: sbom)
    monkeypatch.setattr("genticode.orchestrator.maybe_cyclonedx_npm", lambda root, out: sbom)
    sc = orch.run_supply_pack(tmp_path, tmp_path / ".genticode")
    # One denied per SBOM → 2
    assert sc["license_violations"] == 2
