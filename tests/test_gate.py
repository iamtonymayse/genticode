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
    rc, summary = evaluate(current, baseline, budgets={"static": {"high": 0}})
    assert rc == 2
    assert summary["delta_high"] == 2


def test_gate_no_baseline_pass():
    current = {"packs": [{"name": "static", "counts": {"by_severity": {}}}]}
    rc, summary = evaluate(current, None)
    assert rc == 0


def test_gate_within_budget_pass():
    baseline = {"packs": [{"name": "static", "counts": {"by_severity": {"high": 1}}}]}
    current = {"packs": [{"name": "static", "counts": {"by_severity": {"high": 1}}}]}
    rc, summary = evaluate(current, baseline, budgets={"static": {"high": 0}})
    assert rc == 0
