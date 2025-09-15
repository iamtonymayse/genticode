import importlib.util
from pathlib import Path
import json


def _load(repo_root: Path):
    mod_path = repo_root / "tools/intent_import.py"
    spec = importlib.util.spec_from_file_location("intent_import", mod_path)
    mod = importlib.util.module_from_spec(spec)
    assert spec and spec.loader
    spec.loader.exec_module(mod)  # type: ignore
    return mod


def test_main_dry_run_and_apply(tmp_path):
    repo = Path(__file__).parents[1]
    mod = _load(repo)
    mod.ROOT = tmp_path
    mod.SSOT_DIR = tmp_path / "ssot"
    mod.REQ_PATH = mod.SSOT_DIR / "requirements.yaml"
    mod.DEC_PATH = mod.SSOT_DIR / "decisions.yaml"
    mod.POLICY_PATH = mod.SSOT_DIR / "policy.yaml"

    feed = tmp_path / "feed.jsonl"
    feed.write_text("\n".join([
        json.dumps({"type": "NOTE", "text": "ignore"}),
        json.dumps({"type": "REQ", "data": {"id": "REQ-Z", "title": "Z", "status": "ready", "acceptance": [{"id": "AC-Z", "text": "ok"}]}}),
    ]) + "\n")

    rc = mod.main([str(feed)])
    assert rc == 0
    rc2 = mod.main([str(feed), "--apply"])
    assert rc2 == 0
    assert mod.REQ_PATH.exists()

    bad = tmp_path / "bad.jsonl"
    bad.write_text(json.dumps({"type": "WHAT"}) + "\n")
    rc3 = mod.main([str(bad)])
    assert rc3 == 2


def test_gate_traceability_and_quality_via_import():
    # Import gate here to increase coverage without new files
    from genticode.gate import evaluate
    baseline = {"packs": [{"name": "traceability", "counts": {"uncovered": 3, "ac_ids": 5, "covered": 2}}]}
    current = {"packs": [{"name": "traceability", "counts": {"uncovered": 5, "ac_ids": 5, "covered": 0}}]}
    rc, _ = evaluate(current, baseline, budgets={"traceability": {"uncovered_delta_max": 1}}, phase="new_code_only")
    assert rc == 2
    rc2, _ = evaluate(current, baseline, budgets={"traceability": {"uncovered_max": 5}}, phase="hard")
    assert rc2 == 0
    # quality count budget
    b2 = {"packs": [{"name": "quality", "counts": {"findings": 1}}]}
    c2 = {"packs": [{"name": "quality", "counts": {"findings": 3}}]}
    rcq, _ = evaluate(c2, b2, budgets={"quality": {"count": 1}}, phase="new_code_only")
    assert rcq == 2
