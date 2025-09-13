from pathlib import Path

from genticode import orchestrator as orch
from genticode.gate import evaluate


def test_traceability_coverage_counts(tmp_path):
    # priority with two IDs
    (tmp_path / "PRIORITY.yaml").write_text("ids:\n  - AC_1\n  - AC_2\n")
    # tests referencing only one
    (tmp_path / "tests").mkdir()
    (tmp_path / "tests/test_sample.py").write_text("# AC_1 covered\n")
    counts = orch.run_traceability_pack(tmp_path, tmp_path / ".genticode")
    assert counts["ac_ids"] == 2 and counts["covered"] == 1 and counts["uncovered"] == 1


def test_gate_traceability_budgets():
    baseline = {"packs": [{"name": "traceability", "counts": {"uncovered": 1}}]}
    current = {"packs": [{"name": "traceability", "counts": {"uncovered": 3}}]}
    # hard budget exceeded by absolute uncovered
    rc, _ = evaluate(current, baseline, budgets={"traceability": {"uncovered_max": 2}}, phase="hard")
    assert rc == 2
    # new_code_only with delta budget
    rc2, _ = evaluate(current, baseline, budgets={"traceability": {"uncovered_delta_max": 1}}, phase="new_code_only")
    assert rc2 == 2
    # warn phase returns warn code on exceed
    rc3, _ = evaluate(current, baseline, budgets={"traceability": {"uncovered_delta_max": 1}}, phase="warn")
    assert rc3 == 1
