from __future__ import annotations

from typing import Tuple


def _get_sev_counts(report: dict, pack: str) -> dict:
    for p in (report.get("packs", []) or []):
        if p.get("name") == pack:
            return (p.get("counts", {}).get("by_severity") or {})
    return {}


def evaluate(report: dict, baseline: dict | None, budgets: dict | None = None) -> tuple[int, dict]:
    """Evaluate delta vs baseline under budgets.

    Returns (exit_code, summary)
    exit_code: 0 pass, 1 warn, 2 fail
    """
    budgets = budgets or {"static": {"high": 0}}
    if not baseline:
        return 0, {"reason": "no baseline"}
    cur = _get_sev_counts(report, "static")
    base = _get_sev_counts(baseline, "static")
    cur_h = int(cur.get("high", 0))
    base_h = int(base.get("high", 0))
    delta_new = max(0, cur_h - base_h)
    budget = int(budgets.get("static", {}).get("high", 0))
    if delta_new > budget:
        return 2, {"reason": "new high findings exceed budget", "delta_high": delta_new, "budget": budget}
    return 0, {"reason": "within budget", "delta_high": delta_new}

