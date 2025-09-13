import argparse
import json
import os
import platform
from pathlib import Path

from .report import build_empty_report, write_json, add_pack_summary
from .html import render_html
from .sarif import to_sarif
from .baseline import baseline_capture, baseline_clear, load_suppressions
from .prompt import scan_repo as prompt_scan
from .prompt.manifest import build_manifest, write_manifest
from .static import maybe_run_semgrep, normalize_semgrep
from .gate import evaluate as gate_evaluate
from .policy import load as load_policy
from .supply import maybe_cyclonedx_py, maybe_cyclonedx_npm, evaluate_licenses
from .quality import maybe_run_quality
from .traceability import load_priority
from .log import get_logger
from . import VERSION
from .orchestrator import run_all as run_packs


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
    log = get_logger()
    ensure_layout()
    # Load policy
    try:
        policy = load_policy(GC_DIR / "policy.yaml")
    except Exception as e:
        print(f"Policy error: {e}")
        policy = None
    baseline_present = (GC_DIR / "baseline" / "report.json").exists()
    report = build_empty_report(version=VERSION, baseline_present=baseline_present)
    # Delegate pack execution to orchestrator (policy-aware)
    run_packs(policy, ROOT, GC_DIR, report)
    write_json(GC_DIR / "report.json", report)
    # Gating vs baseline
    base_path = GC_DIR / "baseline" / "report.json"
    baseline = None
    if base_path.exists():
        try:
            baseline = json.loads(base_path.read_text())
        except Exception:
            baseline = None
    # Use policy budgets if available
    suppressions = load_suppressions(GC_DIR)
    rc, _summary = gate_evaluate(
        report,
        baseline,
        budgets=(policy.budgets if policy else None),
        phase=(policy.get_phase() if policy else "new_code_only"),
        suppressions=suppressions,
    )
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
        sarif = to_sarif(data, GC_DIR)
        out = GC_DIR / "sarif.json"
        write_json(out, sarif)
        print(str(out))
    if not args.html and not args.sarif:
        # Default: do both for convenience.
        html = render_html(data)
        (GC_DIR / "report.html").write_text(html)
        sarif = to_sarif(data, GC_DIR)
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


def cmd_iast(_: argparse.Namespace) -> int:
    # Null provider — no-op with success
    print("IAST null provider: no-op")
    return 0


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

    p_iast = sub.add_parser("iast", help="Run IAST checks (null provider)")
    p_iast.set_defaults(func=cmd_iast)

    args = parser.parse_args(argv)
    return int(args.func(args))
