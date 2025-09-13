import argparse
import json
import os
import platform
from pathlib import Path

from .report import build_empty_report, write_json, add_pack_summary
from .html import render_html
from .sarif import to_sarif
from .baseline import baseline_capture, baseline_clear
from .prompt import scan_repo as prompt_scan
from .prompt.manifest import build_manifest, write_manifest
from .static import maybe_run_semgrep, normalize_semgrep
from .gate import evaluate as gate_evaluate
from .supply import maybe_cyclonedx_py, maybe_cyclonedx_npm, evaluate_licenses
from . import VERSION


ROOT = Path(os.getcwd())
GC_DIR = ROOT / ".genticode"


def ensure_layout() -> None:
    (GC_DIR / "logs").mkdir(parents=True, exist_ok=True)
    (GC_DIR / "cache").mkdir(parents=True, exist_ok=True)
    (GC_DIR / "raw").mkdir(parents=True, exist_ok=True)
    (GC_DIR / "reports").mkdir(parents=True, exist_ok=True)
    (GC_DIR / "baseline").mkdir(parents=True, exist_ok=True)
    (GC_DIR / "candidates").mkdir(parents=True, exist_ok=True)
    (GC_DIR / "local").mkdir(parents=True, exist_ok=True)


def cmd_init(_: argparse.Namespace) -> int:
    ensure_layout()
    policy = GC_DIR / "policy.yaml"
    if not policy.exists():
        policy.write_text(
            """# Genticode policy (stub)\n"
            "version: 0\n"
            "packs: {static: false, supply: false, quality: false, traceability: false}\n"
            "budgets: {}\n"
        )
    priority = ROOT / "PRIORITY.yaml"
    if not priority.exists():
        priority.write_text(
            """# PRIORITY.yaml (stub)\n"
            "# Define AC IDs and scopes here.\n"
        )
    print("Initialized .genticode structure and stubs.")
    return 0


def cmd_check(_: argparse.Namespace) -> int:
    ensure_layout()
    baseline_present = (GC_DIR / "baseline" / "report.json").exists()
    report = build_empty_report(version=VERSION, baseline_present=baseline_present)
    # Prompt Hygiene pack scan (MVP)
    spans = prompt_scan(ROOT)
    manifest = build_manifest(spans)
    write_manifest(GC_DIR / "prompts.manifest.json", manifest)
    add_pack_summary(report, pack="prompt", counts={"prompts": len(manifest["items"])})
    # Static pack (Semgrep) — best-effort run
    sg_raw = maybe_run_semgrep(ROOT, GC_DIR / "raw/semgrep.json")
    if sg_raw is not None:
        findings = normalize_semgrep(sg_raw)
        # Compute severity buckets
        sev_counts: dict[str, int] = {}
        for f in findings:
            sev = str(f.get("severity", "info")).lower()
            sev_counts[sev] = sev_counts.get(sev, 0) + 1
        add_pack_summary(report, pack="static", counts={"findings": len(findings), "by_severity": sev_counts})
    else:
        add_pack_summary(report, pack="static", counts={"findings": 0, "by_severity": {}})
    # Supply pack (SBOM + licenses) — best-effort
    sbom_py = maybe_cyclonedx_py(ROOT, GC_DIR / "raw/sbom-python.json")
    sbom_node = maybe_cyclonedx_npm(ROOT, GC_DIR / "raw/sbom-node.json")
    lic_viol = 0
    if sbom_py:
        v, _ = evaluate_licenses(sbom_py)
        lic_viol += v
    if sbom_node:
        v, _ = evaluate_licenses(sbom_node)
        lic_viol += v
    add_pack_summary(report, pack="supply", counts={"license_violations": int(lic_viol)})
    write_json(GC_DIR / "report.json", report)
    # Gating vs baseline
    base_path = GC_DIR / "baseline" / "report.json"
    baseline = None
    if base_path.exists():
        try:
            baseline = json.loads(base_path.read_text())
        except Exception:
            baseline = None
    rc, _summary = gate_evaluate(report, baseline)
    print(str(GC_DIR / "report.json"))
    return rc


def cmd_report(args: argparse.Namespace) -> int:
    ensure_layout()
    report_path = GC_DIR / "report.json"
    if not report_path.exists():
        raise SystemExit(".genticode/report.json not found. Run 'genticode check' first.")
    data = json.loads(report_path.read_text())
    rc = 0
    if args.html:
        html = render_html(data)
        out = GC_DIR / "report.html"
        out.write_text(html)
        print(str(out))
    if args.sarif:
        sarif = to_sarif(data)
        out = GC_DIR / "sarif.json"
        write_json(out, sarif)
        print(str(out))
    if not args.html and not args.sarif:
        # Default: do both for convenience.
        html = render_html(data)
        (GC_DIR / "report.html").write_text(html)
        sarif = to_sarif(data)
        write_json(GC_DIR / "sarif.json", sarif)
        print(str(GC_DIR / "report.html"))
        print(str(GC_DIR / "sarif.json"))
    return rc


def cmd_baseline(args: argparse.Namespace) -> int:
    ensure_layout()
    if args.action == "capture":
        return baseline_capture(GC_DIR)
    elif args.action == "clear":
        return baseline_clear(GC_DIR)
    else:
        raise SystemExit(f"Unknown baseline action: {args.action}")


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="genticode", description="Genticode CLI")
    parser.add_argument("--version", action="version", version=f"genticode {VERSION}")
    sub = parser.add_subparsers(dest="cmd", required=True)

    p_init = sub.add_parser("init", help="Initialize .genticode and stubs")
    p_init.set_defaults(func=cmd_init)

    p_check = sub.add_parser("check", help="Run checks and produce report.json")
    p_check.set_defaults(func=cmd_check)

    p_report = sub.add_parser("report", help="Render HTML/SARIF from report.json")
    p_report.add_argument("--html", action="store_true", help="Write report.html")
    p_report.add_argument("--sarif", action="store_true", help="Write sarif.json")
    p_report.set_defaults(func=cmd_report)

    p_bl = sub.add_parser("baseline", help="Manage baseline store")
    p_bl.add_argument("action", choices=["capture", "clear"], help="Capture or clear baseline")
    p_bl.set_defaults(func=cmd_baseline)

    args = parser.parse_args(argv)
    return int(args.func(args))
