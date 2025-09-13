from __future__ import annotations

from typing import Iterable, Tuple


def _iter_component_licenses(sbom: dict) -> Iterable[str]:
    for comp in (sbom.get("components") or []):
        lic = None
        # CycloneDX license component forms
        licenses = comp.get("licenses") or []
        for l in licenses:
            choice = l.get("license") or {}
            lic = choice.get("id") or choice.get("name")
            if lic:
                yield str(lic)


def evaluate_licenses(sbom: dict, allow: set[str] | None = None, deny: set[str] | None = None, fail_on_unknown: bool = True) -> Tuple[int, dict]:
    allow = allow or {"MIT", "BSD-2-Clause", "BSD-3-Clause", "Apache-2.0"}
    deny = deny or {"AGPL-3.0"}
    violations = []
    unknown = []
    for lic in _iter_component_licenses(sbom):
        if lic in deny:
            violations.append(lic)
        elif lic not in allow and fail_on_unknown:
            unknown.append(lic)
    total = len(violations) + len(unknown)
    return total, {"deny": violations, "unknown": unknown}

