from genticode.gate import evaluate


def test_performance_factor_gate_new_code_only_and_warn():
    baseline = {
        "packs": [
            {"name": "prompt", "counts": {"duration_ms": 100}},
            {"name": "static", "counts": {"duration_ms": 200}},
        ]
    }
    current = {
        "packs": [
            {"name": "prompt", "counts": {"duration_ms": 260}},  # >2.5x
            {"name": "static", "counts": {"duration_ms": 300}},
        ]
    }
    # new_code_only: factor_max 2.0 -> fail
    rc, _ = evaluate(current, baseline, budgets={"performance": {"factor_max": 2.0}}, phase="new_code_only")
    assert rc == 2
    # warn: returns warn code
    rc2, _ = evaluate(current, baseline, budgets={"performance": {"factor_max": 2.0}}, phase="warn")
    assert rc2 == 1


def test_performance_factor_gate_hard():
    baseline = {"packs": [{"name": "static", "counts": {"duration_ms": 100}}]}
    current = {"packs": [{"name": "static", "counts": {"duration_ms": 300}}]}
    rc, _ = evaluate(current, baseline, budgets={"performance": {"factor_max": 2.0}}, phase="hard")
    assert rc == 2


def test_performance_gate_no_baseline_passes():
    current = {"packs": [{"name": "static", "counts": {"duration_ms": 500}}]}
    rc, _ = evaluate(current, None, budgets={"performance": {"factor_max": 2.0}}, phase="new_code_only")
    assert rc == 0
