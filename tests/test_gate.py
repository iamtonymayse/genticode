from genticode.gate import evaluate


def test_gate_delta_new_high_exceeds_budget():
    baseline = {
        "packs": [
            {"name": "static", "counts": {"by_severity": {"high": 1, "medium": 0}}}
        ]
    }
    current = {
        "packs": [
            {"name": "static", "counts": {"by_severity": {"high": 3, "medium": 1}}}
        ]
    }
    rc, summary = evaluate(current, baseline, budgets={"static": {"high": 0}}, phase="new_code_only")
    assert rc == 2


def test_gate_no_baseline_pass():
    current = {"packs": [{"name": "static", "counts": {"by_severity": {}}}]}
    rc, summary = evaluate(current, None)
    assert rc == 0


def test_gate_within_budget_pass():
    baseline = {"packs": [{"name": "static", "counts": {"by_severity": {"high": 1}}}]}
    current = {"packs": [{"name": "static", "counts": {"by_severity": {"high": 1}}}]}
    rc, summary = evaluate(current, baseline, budgets={"static": {"high": 0}}, phase="new_code_only")
    assert rc == 0


def test_gate_no_baseline_bootstrap():
    current = {"packs": [{"name": "static", "counts": {"by_severity": {"high": 5}}}]}
    rc, _ = evaluate(current, None, budgets={"static": {"high": 0}}, phase="new_code_only")
    assert rc == 0


def test_gate_warn_phase_returns_warn_code():
    baseline = {"packs": [{"name": "static", "counts": {"by_severity": {"high": 1}}}]}
    current = {"packs": [{"name": "static", "counts": {"by_severity": {"high": 3}}}]}
    rc, summary = evaluate(current, baseline, budgets={"static": {"high": 0}}, phase="warn")
    assert rc == 1


def test_gate_hard_phase_uses_absolute_counts():
    baseline = {"packs": [{"name": "static", "counts": {"by_severity": {"high": 10}}}]}
    current = {"packs": [{"name": "static", "counts": {"by_severity": {"high": 2}}}]}
    rc, summary = evaluate(current, baseline, budgets={"static": {"high": 1}}, phase="hard")
    assert rc == 2


def test_gate_prompt_delta_suppressed(tmp_path):
    # baseline prompt count 1, current 3 => delta 2, budget 0
    baseline = {"packs": [{"name": "prompt", "counts": {"prompts": 1}}]}
    current = {"packs": [{"name": "prompt", "counts": {"prompts": 3}}]}
    # Without suppression, should fail in new_code_only
    rc, _ = evaluate(current, baseline, budgets={"prompt": {"count": 0}}, phase="new_code_only")
    assert rc == 2
    # With suppression for pack 'prompt', pass
    rc2, _ = evaluate(current, baseline, budgets={"prompt": {"count": 0}}, phase="new_code_only", suppressions=[{"pack": "prompt", "owner": "qa"}])
    assert rc2 == 0
