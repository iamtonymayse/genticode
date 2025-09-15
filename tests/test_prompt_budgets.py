from genticode.gate import evaluate


def test_prompt_lints_budget_delta_and_hard():
    baseline = {
        "packs": [
            {"name": "prompt", "counts": {"lints": {"PROMPT_MISSING_ID": 1}}}
        ]
    }
    current = {
        "packs": [
            {"name": "prompt", "counts": {"lints": {"PROMPT_MISSING_ID": 3, "LONG_URL": 1}}}
        ]
    }
    # delta 2 over budget 0 -> fail in new_code_only
    rc, _ = evaluate(current, baseline, budgets={"prompt": {"lints": {"PROMPT_MISSING_ID": 0}}}, phase="new_code_only")
    assert rc == 2
    # hard: absolute count <= budget passes
    rc2, _ = evaluate(current, baseline, budgets={"prompt": {"lints": {"PROMPT_MISSING_ID": 3}}}, phase="hard")
    assert rc2 == 0


def test_prompt_lints_budget_warn():
    baseline = {"packs": [{"name": "prompt", "counts": {"lints": {"PROMPT_MISSING_ID": 0}}}]}
    current = {"packs": [{"name": "prompt", "counts": {"lints": {"PROMPT_MISSING_ID": 1}}}]}
    rc, _ = evaluate(current, baseline, budgets={"prompt": {"lints": {"PROMPT_MISSING_ID": 0}}}, phase="warn")
    assert rc == 1
