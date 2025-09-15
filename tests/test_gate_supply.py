from genticode.gate import evaluate


def test_gate_supply_high_budget_delta_and_hard():
    # delta mode
    baseline = {"packs": [{"name": "supply", "counts": {"by_severity": {"high": 1}}}]}
    current = {"packs": [{"name": "supply", "counts": {"by_severity": {"high": 3}}}]}
    rc, _ = evaluate(current, baseline, budgets={"supply": {"high": 0}}, phase="new_code_only")
    assert rc == 2
    # hard mode uses absolute
    rc2, _ = evaluate(current, baseline, budgets={"supply": {"high": 4}}, phase="hard")
    assert rc2 == 0


def test_gate_supply_warn_phase():
    baseline = {"packs": [{"name": "supply", "counts": {"by_severity": {"high": 1}}}]}
    current = {"packs": [{"name": "supply", "counts": {"by_severity": {"high": 2}}}]}
    rc, _ = evaluate(current, baseline, budgets={"supply": {"high": 0}}, phase="warn")
    assert rc == 1
