# AC Evidence — Sprint 0.4a (Baselines & Gates)

- AC: Baseline capture/clear — ✅
  - `genticode baseline capture|clear` manages `.genticode/baseline/`
- AC: Gate engine with budgets and exit codes — ✅
  - Implemented delta evaluation for `static` high severity
  - Exit codes: 0 pass, 2 fail when new highs exceed budget
  - Unit tests validate delta math
- AC: HTML/SARIF emitted in CI (on pass/fail) — ✅
  - `genticode report --html` and `--sarif` work independent of gate

Artifacts
- `.genticode/report.json`, `.genticode/report.html`, `.genticode/sarif.json`

Notes
- Default budget: static.high=0 new above baseline (configurable in future sprints).
