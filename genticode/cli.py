import argparse
import json
import os
import platform
from pathlib import Path

from .report import build_empty_report, write_json
from .html import render_html
from .sarif import to_sarif
from .baseline import baseline_capture, baseline_clear
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
    write_json(GC_DIR / "report.json", report)
    print(str(GC_DIR / "report.json"))
    return 0


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

