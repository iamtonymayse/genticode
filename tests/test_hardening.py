import os, time
from pathlib import Path

from genticode.orchestrator import run_all, PackRunner
from genticode.policy import PolicyConfig, PackConfig


def test_orchestrator_enforces_timeouts(tmp_path):
    def slow_runner(root: Path, gc: Path, policy=None):
        time.sleep(0.5)
        return {"ok": True}

    packs = {"slow": PackRunner("slow", slow_runner)}
    pol = PolicyConfig()
    pol.packs = {"slow": PackConfig(enabled=True, timeout_s=0)}
    report = {"packs": []}
    out = run_all(pol, tmp_path, tmp_path / ".genticode", report, packs=packs)
    slow = next(p for p in out["packs"] if p["name"] == "slow")
    assert slow["counts"].get("error") == "timeout"


def test_large_files_skipped_in_scanners(tmp_path, monkeypatch):
    big = tmp_path / "big.py"
    # Create a large file with prompt-like content
    big.write_text("You are a bot\n" + ("A" * 2_000_000))
    small = tmp_path / "small.py"
    small.write_text("PROMPT='''You are a helper'''\n")
    # Constrain size limit small to force skip
    monkeypatch.setenv("GENTICODE_MAX_FILE_BYTES", "1000")
    from genticode import orchestrator as orch

    counts = orch.run_prompt_pack(tmp_path, tmp_path / ".genticode")
    # Only small file should be counted
    assert counts["prompts"] == 1
