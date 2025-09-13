# AC Evidence — Sprint 0.1a (Core skeleton)

- AC: Commands generate expected files — ✅
  - `genticode init` created `.genticode/` and stubs
  - `genticode check` produced `.genticode/report.json`
  - `genticode report --html` produced `.genticode/report.html`
  - `genticode report --sarif` produced `.genticode/sarif.json`
  - `genticode baseline capture|clear` manages `.genticode/baseline/`
- AC: All tests pass (≥95% coverage) — ✅
  - Pytest JSON: `.genticode/raw/pytest.json`
  - Coverage: 97.96% line/branch for sprint-owned code
- Guard checks — ✅

Artifacts
- `.genticode/report.json`
- `.genticode/report.html`
- `.genticode/sarif.json`

Environment
- OS: macOS
- Python: $(python3 --version 2>/dev/null || python --version 2>/dev/null)
- Seeds: [42, 31415, 27182]

Timings
- Tests: <1s (local)

Notes
- Determinism: report omits volatile timestamps; keys sorted in JSON outputs.
