# Genticode v0.9.6 — Release Notes

Genticode v0.9.6 delivers a robust multi‑pass failing‑tests rubric, stronger test‑hygiene guardrails, and operational hardening while preserving v0.9 parity across packs.

## Highlights
- Multi‑pass attempts loop
  - `scripts/attempt.py`: runs full pytest with time caps and coverage, writes attempt artifacts:
    - JSON: `.genticode/local/attempts/attempt-N.json`
    - Markdown: `.genticode/reports/attempt-N.md`
  - `scripts/lessons_decide.py`: compares two attempts and outputs `RETRY` if >50% failure classes are new; otherwise `SPLIT`.
- Test safety guardrails
  - `scripts/guard.sh` blocks all test deletions and any test edits without an approved waiver file under `.genticode/local/waivers/*.yaml` (must include `approved: true`).
- Orchestrator hardening
  - Packs run in parallel with per‑pack timeouts sourced from policy (`packs.<name>.timeout_s`); timeouts surface as `{error: "timeout"}` in `report.json`.
  - Scanners skip very large files via `GENTICODE_MAX_FILE_BYTES` (default 1 MiB) to keep runs predictable.
- Stabilization preserved
  - Policy engine + budgets/phases, baseline/delta + suppressions, unified SARIF, Static (Semgrep + secrets/PII), Supply (pip‑audit + npm audit + licenses), Quality (ruff/eslint mapped + flake utility), Traceability coverage + uncovered budgets.

## Quickstart
```
python -m genticode init
python -m genticode check
python -m genticode report --html --sarif
```

## Attempts Loop — Commands
```
# Full suite with caps and coverage → JSON report
CAP=1200 ./run "pytest -q --maxfail=0 --disable-warnings --timeout=30 \
  --cov --cov-branch --cov-fail-under=95 \
  --json-report --json-report-file=.genticode/raw/pytest.json"

# Record attempt summary (JSON + Markdown)
python scripts/attempt.py

# Decide retry vs split
python scripts/lessons_decide.py \
  --prev .genticode/local/attempts/attempt-2.json \
  --curr .genticode/local/attempts/attempt-3.json
# → prints: RETRY (X% new classes) or SPLIT (Y% new classes)
```

## Test‑Edit Waivers (required for any changes under tests/)
`.genticode/local/waivers/test-change-YYYYMMDD-<sprint>.yaml` (git‑ignored):
```
approved: true
sprint: <id>
reason: "<why the test was wrong>"
evidence: "<link to AC/spec proving mismatch>"
scope: ["tests/path_or_file"]
expires: "<YYYY-MM-DD>"
owner: "<name>"
```

## Policy Example
```
version: 1
progressive_enforcement: { phase: new_code_only }
packs:
  static: { enabled: true, timeout_s: 300, ruleset: ["p/python", "p/typescript"] }
  supply: { enabled: true, timeout_s: 300 }
  quality:{ enabled: true, timeout_s: 120 }
  prompt: { enabled: true, timeout_s: 120 }
  traceability: { enabled: true, timeout_s: 60 }
budgets:
  static: { high: 0 }
  prompt: { count: 100 }
  quality: { count: 500 }
  supply: { count: 0 }
  traceability: { uncovered_delta_max: 0 }
```

## Environment & Compatibility
- Python 3.10+; macOS and Linux
- Optional tools improve results: semgrep, ruff, eslint, pip‑audit, npm
- Large file limit: set `GENTICODE_MAX_FILE_BYTES` (bytes) if needed

## Artifacts
- `.genticode/report.json`, `.genticode/report.html`, `.genticode/sarif.json`
- Attempts: `.genticode/local/attempts/*`, `.genticode/reports/attempt-*.md`

## Links
- Attempt runner: `scripts/attempt.py`
- Decision helper: `scripts/lessons_decide.py`
- Guard: `scripts/guard.sh`
- README (policy example & usage): `README.md`
