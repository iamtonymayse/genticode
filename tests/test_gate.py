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
    assert summary["delta_high"] == 2


def test_gate_no_baseline_pass():
    current = {"packs": [{"name": "static", "counts": {"by_severity": {}}}]}
    rc, summary = evaluate(current, None)
    assert rc == 0


def test_gate_within_budget_pass():
    baseline = {"packs": [{"name": "static", "counts": {"by_severity": {"high": 1}}}]}
    current = {"packs": [{"name": "static", "counts": {"by_severity": {"high": 1}}}]}
    rc, summary = evaluate(current, baseline, budgets={"static": {"high": 0}}, phase="new_code_only")
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
