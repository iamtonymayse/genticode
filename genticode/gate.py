from __future__ import annotations

from typing import Tuple


def _get_sev_counts(report: dict, pack: str) -> dict:
    for p in (report.get("packs", []) or []):
        if p.get("name") == pack:
            return (p.get("counts", {}).get("by_severity") or {})
    return {}


PACK_COUNT_KEYS = {
    "prompt": "prompts",
    "static": "findings",
    "supply": "license_violations",
    "quality": "findings",
    "traceability": "ac_ids",
}


def _get_pack_count(report: dict, pack: str) -> int:
    key = PACK_COUNT_KEYS.get(pack)
    if not key:
        return 0
    for p in (report.get("packs", []) or []):
        if p.get("name") == pack:
            return int((p.get("counts", {}) or {}).get(key, 0))
    return 0


def evaluate(report: dict, baseline: dict | None, budgets: dict | None = None, phase: str | None = None, suppressions: list[dict] | None = None) -> tuple[int, dict]:
    """Evaluate delta vs baseline under budgets.

    Returns (exit_code, summary)
    exit_code: 0 pass, 1 warn, 2 fail
    """
    budgets = budgets or {"static": {"high": 0}}
    phase = (phase or "new_code_only").lower()
    sup_packs = {s.get("pack") for s in (suppressions or [])}

    # No baseline → pass for non-hard phases to bootstrap
    if baseline is None and phase != "hard":
        return 0, {"reason": "no baseline"}

    # Evaluate static via severity first
    cur = _get_sev_counts(report, "static")
    base = _get_sev_counts(baseline or {}, "static")
    cur_h = int(cur.get("high", 0))
    base_h = int(base.get("high", 0))
    budget_h = int(budgets.get("static", {}).get("high", 0))

    def decide(delta: int, budget: int, pack: str) -> int:
        if pack in sup_packs and delta > 0:
            return 0
        if delta > budget:
            return 1 if phase == "warn" else 2
        return 0

    # hard: absolute
    if phase == "hard":
        rc = decide(cur_h, budget_h, "static")
    else:
        rc = decide(max(0, cur_h - base_h), budget_h, "static")

    # Evaluate Traceability uncovered if budgeted
    tb = (budgets.get("traceability") if budgets else None) or {}
    if tb:
        # current and baseline uncovered
        def _uncovered(d: dict | None) -> int:
            if not d:
                return 0
            for p in (d.get("packs", []) or []):
                if p.get("name") == "traceability":
                    return int((p.get("counts", {}) or {}).get("uncovered", 0))
            return 0

        cur_u = _uncovered(report)
        base_u = _uncovered(baseline or {})
        abs_budget = tb.get("uncovered_max")
        delta_budget = tb.get("uncovered_delta_max")
        if phase == "hard" and abs_budget is not None and cur_u > int(abs_budget):
            rc = max(rc, 2)
        if phase != "hard" and delta_budget is not None and max(0, cur_u - base_u) > int(delta_budget):
            rc = max(rc, 1 if phase == "warn" else 2)

    # Evaluate other packs by count if budgets provided
    for pack, key in PACK_COUNT_KEYS.items():
        if pack == "static":
            continue
        if pack == "traceability":
            continue
        b = budgets.get(pack) if budgets else None
        if not b:
            continue
        budget_count = int(b.get("count", 0))
        cur_c = _get_pack_count(report, pack)
        base_c = _get_pack_count(baseline or {}, pack)
        delta = cur_c if phase == "hard" else max(0, cur_c - base_c)
        rc = max(rc, decide(delta, budget_count, pack))

    return rc, {"phase": phase}
