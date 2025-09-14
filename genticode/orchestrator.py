from __future__ import annotations

from dataclasses import dataclass
import concurrent.futures as cf
import os
from pathlib import Path
from typing import Callable, Dict

from .report import add_pack_summary
from .prompt import scan_repo as prompt_scan
from .prompt.manifest import build_manifest, write_manifest
from .static import maybe_run_semgrep, normalize_semgrep
from .supply import maybe_cyclonedx_py, maybe_cyclonedx_npm, evaluate_licenses
from .supply.vuln import maybe_pip_audit, maybe_npm_audit, normalize_pip_audit, normalize_npm_audit
from .quality import maybe_run_quality
from .traceability import load_priority
from .traceability.parser import scan_test_coverage


@dataclass
class PackRunner:
    name: str
    func: Callable[[Path, Path, object | None], dict]


def run_prompt_pack(root: Path, gc_dir: Path, policy=None) -> dict:
    spans = prompt_scan(root)
    manifest = build_manifest(spans)
    write_manifest(gc_dir / "prompts.manifest.json", manifest)
    # Emit spans for IDE surfacing
    (gc_dir / "raw").mkdir(parents=True, exist_ok=True)
    (gc_dir / "raw" / "spans.json").write_text(
        __import__("json").dumps(
            [
                {"file": it["file"], "start": it["start"], "end": it["end"], "pack": "prompt"}
                for it in manifest.get("items", [])
            ],
            indent=2,
        )
        + "\n"
    )
    return {"prompts": len(manifest["items"])}


def run_static_pack(root: Path, gc_dir: Path, policy=None) -> dict:
    # derive ruleset configs from policy.pack["static"].ruleset (str or list)
    configs = None
    if getattr(policy, "packs", None) and "static" in policy.packs and policy.packs["static"].ruleset:
        rs = policy.packs["static"].ruleset
        configs = [rs] if isinstance(rs, str) else list(rs)
    sg_raw = maybe_run_semgrep(root, gc_dir / "raw/semgrep.json", configs=configs)
    if sg_raw is None:
        counts = {"findings": 0, "by_severity": {}}
    else:
        findings = normalize_semgrep(sg_raw)
        sev_counts: dict[str, int] = {}
        for f in findings:
            sev = str(f.get("severity", "info")).lower()
            sev_counts[sev] = sev_counts.get(sev, 0) + 1
        counts = {"findings": len(findings), "by_severity": sev_counts}
    # secrets/PII detector
    from .static.secrets import scan_repo_for_secrets
    secrets = scan_repo_for_secrets(root)
    counts["secrets"] = len(secrets)
    # Count secrets as high severity for budgets
    counts.setdefault("by_severity", {})
    counts["by_severity"]["high"] = counts["by_severity"].get("high", 0) + len(secrets)
    return counts


def _has_any(root: Path, names: list[str]) -> bool:
    for n in names:
        if (root / n).exists():
            return True
    return False


def run_supply_pack(root: Path, gc_dir: Path, policy=None) -> dict:
    # Lockfile-only SBOM provenance (MPI): run only when lockfiles present
    py_lock = _has_any(root, [
        "requirements.lock",
        "requirements.txt",  # allow minimal case during bootstrap
        "poetry.lock",
        "uv.lock",
        "pip-tools.lock",
    ])
    node_lock = _has_any(root, [
        "package-lock.json",
        "pnpm-lock.yaml",
        "yarn.lock",
    ])
    sbom_py = maybe_cyclonedx_py(root, gc_dir / "raw/sbom-python.json") if py_lock else None
    sbom_node = maybe_cyclonedx_npm(root, gc_dir / "raw/sbom-node.json") if node_lock else None
    lic_viol = 0
    if sbom_py:
        v, _ = evaluate_licenses(sbom_py)
        lic_viol += v
    if sbom_node:
        v, _ = evaluate_licenses(sbom_node)
        lic_viol += v
    # Vulnerabilities
    vulns_total = 0
    by_sev: dict[str, int] = {}
    pa = maybe_pip_audit(root, gc_dir / "raw/pip-audit.json")
    if pa:
        for v in normalize_pip_audit(pa):
            vulns_total += 1
            s = v.get("severity", "info")
            by_sev[s] = by_sev.get(s, 0) + 1
    na = maybe_npm_audit(root, gc_dir / "raw/npm-audit.json")
    if na:
        for v in normalize_npm_audit(na):
            vulns_total += 1
            s = v.get("severity", "info")
            by_sev[s] = by_sev.get(s, 0) + 1
    comp_py = len((sbom_py or {}).get("components", []) or [])
    comp_node = len((sbom_node or {}).get("components", []) or [])
    return {
        "license_violations": int(lic_viol),
        "vulns": vulns_total,
        "by_severity": by_sev,
        "components": {"python": comp_py, "node": comp_node},
        "sbom_present": bool(sbom_py or sbom_node),
    }


def run_quality_pack(root: Path, gc_dir: Path, policy=None) -> dict:
    return maybe_run_quality(root)


def run_traceability_pack(root: Path, gc_dir: Path, policy=None) -> dict:
    pr = load_priority(root / "PRIORITY.yaml")
    ids = pr.get("ids", []) or []
    cov_map = scan_test_coverage(root, ids)
    covered = sum(1 for k, v in cov_map.items() if v > 0)
    uncovered = max(0, len(ids) - covered)
    return {"ac_ids": len(ids), "covered": covered, "uncovered": uncovered}


DEFAULT_PACKS: Dict[str, PackRunner] = {
    "prompt": PackRunner("prompt", run_prompt_pack),
    "static": PackRunner("static", run_static_pack),
    "supply": PackRunner("supply", run_supply_pack),
    "quality": PackRunner("quality", run_quality_pack),
    "traceability": PackRunner("traceability", run_traceability_pack),
}


def run_all(policy, root: Path, gc_dir: Path, report: dict, packs: Dict[str, PackRunner] | None = None) -> dict:
    packs = packs or DEFAULT_PACKS
    tasks = []
    with cf.ThreadPoolExecutor(max_workers=max(1, min(8, (os.cpu_count() or 2)))) as ex:
        for name, runner in packs.items():
            # Respect policy pack enable flag when present
            enabled = True
            timeout_s = 600
            if getattr(policy, "packs", None) and name in policy.packs:
                pcfg = policy.packs[name]
                enabled = bool(pcfg.enabled)
                timeout_s = int(getattr(pcfg, "timeout_s", timeout_s))
            if not enabled:
                continue
            fut = ex.submit(runner.func, root, gc_dir, policy)
            tasks.append((name, fut, timeout_s))

        for name, fut, timeout_s in tasks:
            try:
                counts = fut.result(timeout=timeout_s)
                add_pack_summary(report, pack=name, counts=counts or {})
            except cf.TimeoutError:
                add_pack_summary(report, pack=name, counts={"error": "timeout", "timeout_s": timeout_s})
            except Exception as e:  # noqa: BLE001 — continue on pack failure
                add_pack_summary(report, pack=name, counts={"error": str(e)})
    return report
