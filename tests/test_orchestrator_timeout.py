import time
from pathlib import Path

from genticode.orchestrator import run_all, PackRunner
from genticode.policy import PolicyConfig, PackConfig


def test_orchestrator_pack_timeout_recorded(tmp_path: Path):
    def slow_runner(root: Path, gc: Path, policy=None):
        time.sleep(0.2)
        return {"ok": 1}

    packs = {
        "slow": PackRunner("slow", slow_runner),
    }
    pol = PolicyConfig()
    # very small timeout to trigger TimeoutError (coerced to int → 0)
    pol.packs = {"slow": PackConfig(enabled=True, timeout_s=0)}
    report = {"packs": []}
    run_all(pol, tmp_path, tmp_path / ".genticode", report, packs=packs)
    summary = {p["name"]: p for p in report["packs"]}
    assert "slow" in summary
    counts = summary["slow"]["counts"]
    assert counts.get("error") == "timeout" and counts.get("timeout_s") == 0
