from __future__ import annotations

from typing import Tuple


def _get_sev_counts(report: dict, pack: str) -> dict:
    for p in (report.get("packs", []) or []):
        if p.get("name") == pack:
            return (p.get("counts", {}).get("by_severity") or {})
    return {}


def evaluate(report: dict, baseline: dict | None, budgets: dict | None = None, phase: str | None = None) -> tuple[int, dict]:
    """Evaluate delta vs baseline under budgets.

    Returns (exit_code, summary)
    exit_code: 0 pass, 1 warn, 2 fail
    """
    budgets = budgets or {"static": {"high": 0}}
    phase = (phase or "new_code_only").lower()
    cur = _get_sev_counts(report, "static")
    base = _get_sev_counts(baseline or {}, "static")
    cur_h = int(cur.get("high", 0))
    base_h = int(base.get("high", 0))
    budget = int(budgets.get("static", {}).get("high", 0))

    if phase == "hard":
        # Enforce absolute counts regardless of baseline
        if cur_h > budget:
            return 2, {"reason": "hard budget exceeded", "current_high": cur_h, "budget": budget}
        return 0, {"reason": "within hard budget", "current_high": cur_h}

    # new_code_only or warn use delta vs baseline
    delta_new = max(0, cur_h - base_h)
    if delta_new > budget:
        if phase == "warn":
            return 1, {"reason": "delta exceeds budget (warn)", "delta_high": delta_new, "budget": budget}
        return 2, {"reason": "delta exceeds budget (fail)", "delta_high": delta_new, "budget": budget}
    return 0, {"reason": "within budget", "delta_high": delta_new}
