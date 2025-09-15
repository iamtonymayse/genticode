# ROADMAP_SSOT_TRACE_GOLDENS.md
**Release:** v0.8.x (minor)  
**Theme:** End-to-end golden harnesses for SSOT → TRACE

## Objective
Prove determinism and provenance by reusing the viewer line model in tests, with byte-stable artifacts and per-line source mapping.

## Scope
- Define viewer contract (lines[], steps{}, groups{}, provenance).
- Emit `TRACE.json` per agent with line-level provenance.
- Golden harness: build viewer lines and assert stable IDs/text/groups.
- Determinism checks: fresh clone, two runs → identical TRACE/PSM.
- CI integration: upload goldens; fail on drift with friendly diff UI.

## Deliverables
- `TRACE.json` + `PSM.json` (prompt source map) per build.
- Test helpers to diff per-line provenance.
- Docs: viewer contract, test recipes, and troubleshooting.

## Acceptance Criteria
- Re-run on same inputs yields identical TRACE + PSM (ignoring timestamps).
- Every output line maps back to at least one SSOT fragment and pass ID.
- CI presents minimal diff for any drift (line text or provenance IDs).

## Risks
- Hidden whitespace variance → normalize whitespace + endlines in emitters.
- Parser drift vs. renderer → reuse the same line-builder in tests.

## Milestones
- **M1** Contract + emitters  
- **M2** Golden tests + helpers  
- **M3** CI wiring + docs