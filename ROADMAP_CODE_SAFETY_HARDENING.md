# ROADMAP_CODE_SAFETY_HARDENING.md
**Release:** v0.8.x (minor)  
**Theme:** Secure & Robust Codebase Hardening

## Objective
Harden the pipeline and outputs: enforce gates, unify schemas, integrate SAST/SBOM, and ship clear reports.

## Scope
- CI gates: contract tests, feature map, scope guard, thresholds.
- Unified schema: `findings.json` + strict normalization.
- Compare: stable, human-first diff views + SARIF/HTML.
- Performance controls: `--parallel`, global/per-tool time caps.
- SAST: Semgrep rulepacks (Py/TS); SBOM: CycloneDX + vuln map.
- Logging: redaction by default, JSONL trace, permissions review.
- Reports: HTML, SARIF, JSON with stable paths under `.genticode/`.

## Deliverables
- Green compile + passing acceptance checks.
- Single CLI (`genti`) with `scan`, `normalize`, `compare`, `report`.
- CI job with baseline precedence and nightly “drift” run.
- Docs: CI quickstart + gate cookbook.

## Acceptance Criteria
- Any high-severity finding triggers non-zero exit when configured.
- Normalizer emits schema-valid JSON; compare highlights deltas only.
- SBOM includes versions + CVE joins; Semgrep runs within time caps.
- Reports render locally without network access.

## Risks
- Rulepack noise → ship curated baseline + suppression guide.
- Path portability → default to `.genticode/` root with relative links.
- Mac/Linux differences → use coreutils-compatible commands in docs.

## Milestones
- **M1** CI gates + schema strictness  
- **M2** SAST + SBOM integration  
- **M3** Reports + portability polish