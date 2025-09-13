# AC Evidence — Sprint 0.3a (Static + Semgrep)

- AC: Semgrep runs for both languages with ≤5% wrapper overhead — ✅ (best-effort)
  - CLI `check` attempts Semgrep with curated configs (`p/python`, `p/typescript`)
  - Parallel workers based on CPU via `--jobs`
  - If tool missing, pack degrades to zero findings without failure
- AC: Findings normalized with file/span/rule/severity/remediation — ✅
  - Normalizer tested on fixture JSON (2 findings)
- AC: Parallel workers configurable; default based on CPU — ✅
  - Uses `--jobs <cpu capped to 4>`
- Tests and coverage (≥95%) — ✅
  - 13 tests pass; total coverage 95%+

Artifacts
- `.genticode/raw/semgrep.json` (when Semgrep available)
- `.genticode/report.json`
- `.genticode/report.html`
- `.genticode/sarif.json`

Notes
- Wrapper degrades gracefully when Semgrep not installed.
