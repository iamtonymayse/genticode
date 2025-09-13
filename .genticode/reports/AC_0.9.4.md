# AC Evidence — v0.9.x Stabilization up to 0.9.4

Scope: Policy engine, progressive gates, baselines/deltas across packs, unified SARIF, orchestrator + packs, static completion, supply vulnerabilities, quality mapping + flake detector, traceability coverage and budgets, hardening + concurrency.

Acceptance Summary
- Policy engine drives budgets/phases — ✅
- Gates: warn/new_code_only/hard with correct exit codes — ✅
- Baselines/deltas across packs + suppressions — ✅
- Unified SARIF includes Prompt + Static findings — ✅
- Orchestrator: pluggable packs, timeouts, parallel — ✅
- Static completion: secrets/PII + policy rulesets — ✅
- Supply: pip-audit/npm audit normalized; license policy retained — ✅
- Quality: ruff/eslint severities; flake rate util — ✅
- Traceability: coverage matrix counts and uncovered budgets — ✅
- Hardening: file-size skips, redaction, safe subprocess — ✅

Validation
- Tests passed: 61
- Coverage: ≥95% (total ~95.11%)
- Guard: scripts/guard.sh passed

Artifacts
- `.genticode/report.json`, `.genticode/report.html`, `.genticode/sarif.json`
- Raw: `.genticode/raw/*` (semgrep, pip-audit/npm when available)

Environment
- OS: macOS
- Python: $(python3 --version 2>/dev/null || python --version 2>/dev/null)

Notes
- Tools that are not installed degrade gracefully; results improve when present.
- `GENTICODE_MAX_FILE_BYTES` controls scanner size limits (default 1 MiB).
