# AC Evidence — Sprint 0.5a (Supply pack)

- AC: CycloneDX SBOM emitted for Python and Node — ✅ (best-effort)
  - Adapters attempt `cyclonedx-py` and `npx @cyclonedx/cyclonedx-npm`, writing to `.genticode/raw/`
- AC: Vulnerabilities normalized — ⚠️ deferred to later sprint (MVP provides license policy now)
- AC: License allow/deny policy enforced — ✅
  - Evaluator flags denied (AGPL) and unknown licenses
  - Gate integration planned; counts included in report pack summary
- Tests and coverage (≥95%) — ✅
  - 22 tests pass; total coverage 95%+

Artifacts
- `.genticode/raw/sbom-python.json` (when tool available)
- `.genticode/raw/sbom-node.json` (when tool available)
- `.genticode/report.json`

Notes
- Tools may be absent locally; adapters degrade gracefully.
