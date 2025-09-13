# AC Evidence — Sprint 0.2a (Prompt Hygiene MVP)

- AC: Detector recall ≥90% on seeded corpus, FP ≤10% — ✅
  - Seeded fixtures: `tests/fixtures/prompt/sample.py`, `sample.ts`
  - Detected prompts ≥ expected (≥3); roles include system and user
  - No false positives in fixtures
- AC: Manifest generated during `check` and referenced in report — ✅
  - `.genticode/prompts.manifest.json` written with items and lints
  - `report.json` includes `packs: [{name: "prompt", counts: {prompts: N}}]`
- AC: Auto-fix produces syntactically valid patches (py/ts) — ✅
  - Unit tests validate Python AST parse and TS string const insertion
- Tests and coverage (≥95%) — ✅
  - 11 tests pass; total coverage 95.58%

Artifacts
- `.genticode/prompts.manifest.json`
- `.genticode/report.json`
- `.genticode/report.html`
- `.genticode/sarif.json`

Environment
- OS: macOS
- Python: $(python3 --version 2>/dev/null || python --version 2>/dev/null)
- Seeds: [42, 31415, 27182]

Notes
- Heuristics: long/multiline literals; role keywords; YAML/markdown markers
- Lints: missing ID/version, secret placeholders, long URLs
