# Sprint Plan v0.9 — Genticode Greenfield (v2)

Feature and Review sprints alternate. Minimal plausible implementation (MPI). **>95% coverage** for sprint-owned code.

## Global working rules
- Read lessons first: if present, read `.genticode/local/LESSONS_CURRENT.md` and apply its checklists.
- Checkpoints: before each Feature sprint, tag `pre-<sprint-id>`. On failure, `git reset --hard pre-<sprint-id>` and retry after updating lessons.
- Coverage: ≥95% line and branch for sprint-owned packages.
- One report: converge to `.genticode/report.json` once features land.
- Environments: macOS/Linux, Python 3.10+, Node 18+.

## Lessons workflow (compatible with future Genticode)
- Files (git-ignored): `.genticode/local/LESSONS.md`, `LESSONS_CURRENT.md`, `LESSONS_ACCEPTED.md`, `LESSONS_GUIDE.md`.
- During Review:
  1) Record lessons in `LESSONS.md` using the template from `LESSONS_GUIDE.md`.
  2) Merge: de-duplicate and mark superseded items. Produce `LESSONS_CURRENT.md` as the active set.
  3) If the Feature sprint is accepted and lessons were applied, append those lesson entries to `LESSONS_ACCEPTED.md` under the sprint heading.
- During next Feature: read `LESSONS_CURRENT.md` first and apply the relevant checklists.

## Root-cause checklist (use in every Review)
- Classify defect; write a short 5-Whys; capture evidence (failing test, repro); define **improved instructions** and **preventive controls**; mark superseded items.

## Effort and thinking level per sprint (aim ≥95% success)
| Sprint | Thinking | Agent-hours | Human-hours | Success P(≥) |
|---|---|---:|---:|---:|
| 0.1a Core skeleton | Low | 0.5–1 | 0.2 | 0.99 |
| 0.1b Review | Low | 0.2 | 0.2 | 1.00 |
| 0.2a Prompt Hygiene MVP | Medium | 4–6 | 0.5 | 0.96 |
| 0.2b Review | Low | 0.5 | 0.3 | 0.99 |
| 0.3a Static + Semgrep | Medium | 3–4 | 0.5 | 0.97 |
| 0.3b Review | Low | 0.4 | 0.3 | 0.99 |
| 0.4a Baselines & Gates | Medium | 3 | 0.5 | 0.96 |
| 0.4b Review | Low | 0.4 | 0.3 | 0.99 |
| 0.5a Supply pack | Medium | 4–6 | 0.6 | 0.95 |
| 0.5b Review | Low | 0.6 | 0.3 | 0.99 |
| 0.6a Quality + Reports | Medium | 3–4 | 0.6 | 0.96 |
| 0.6b Review | Low | 0.4 | 0.3 | 0.99 |
| 0.7a Traceability | Medium | 3–5 | 0.6 | 0.95 |
| 0.7b Review | Low | 0.6 | 0.3 | 0.99 |
| 0.8a IDE/Perf/Logging | Medium | 3 | 0.6 | 0.96 |
| 0.8b Review | Low | 0.4 | 0.3 | 0.99 |
| 0.9a Parity/Packaging/IAST null | Medium | 4–6 | 0.8 | 0.95 |
| 0.9b Final review | Low | 1 | 0.5 | 0.99 |

> Thinking levels: Low = straightforward coding and wiring; Medium = multi-adapter integration with normalization and tests.

---

## Sprint 0.1a — Core skeleton (Feature)
Goal: scaffold CLI, config layout, normalized artifact placeholders.
- Spec: `init|check|report --html|baseline capture|clear` stubs; create `.genticode/*`; placeholder `report.json` and HTML.
- Agent: implement CLI dispatch, deterministic files, Makefile, CI skeleton; add git-ignore for `.genticode/local/`.
- Tests: CLI routing; file creation; JSON/HTML snapshots; coverage ≥95%.
- Acceptance: commands generate expected files; all tests pass; tag `milestone-0.1`.

## Sprint 0.1b — Core skeleton review (Review)
- Run CI; if failures, record lessons, merge `LESSONS_CURRENT.md`; decide rollback to `pre-0.1a`.

## Sprint 0.2a — Prompt Hygiene MVP (Feature)
Goal: detect prompt-like strings; emit `prompts.manifest.json` and findings.
- Spec: Python + TS/JS heuristics; manifest schema; lints for IDs, versions, secrets, long URLs; safe autofix.
- Agent: AST/token scans; hashing; normalizer; autofix for constants and redaction.
- Tests: golden corpora; property tests; CLI integration; coverage ≥95%.
- Acceptance: recall ≥90%, FP ≤10%; artifacts valid; tag `milestone-0.2`.

## Sprint 0.2b — Prompt Hygiene review (Review)
- Validate corpus; update lessons and `LESSONS_CURRENT.md`; rollback if AC missed.

## Sprint 0.3a — Static + Semgrep (Feature)
Goal: curated rules, secrets, unsafe configs, normalization.
- Spec: run Semgrep both languages; unified severities; parallel workers.
- Agent: vendor rules; map output to normalized findings; deduplicate overlaps.
- Tests: fixtures → snapshots; E2E small repos; coverage ≥95%.
- Acceptance: correct mapping; ≤5% overhead; tag `milestone-0.3`.

## Sprint 0.3b — Static pack review (Review)
- Tune noise; document suppressions; update lessons; rollback if perf/noise off.

## Sprint 0.4a — Baselines & Gates (Feature)
Goal: baseline store, budgets, exit codes, CI examples.
- Spec: baseline capture/clear; gate engine with phases; HTML/SARIF on fail.
- Agent: implement delta evaluation; budgets; exit codes 0/1/2.
- Tests: budget math; delta E2E; coverage ≥95%.
- Acceptance: CI fails on new criticals; tag `milestone-0.4`.

## Sprint 0.4b — Gates review (Review)
- Review false positives; tune budgets; merge lessons; rollback if misfires.

## Sprint 0.5a — Supply pack (Feature)
Goal: SBOM, vuln import, license gate.
- Spec: CycloneDX for pip/poetry and npm/yarn; license allow/deny + unknown fail.
- Agent: adapters; advisory normalizer; license evaluator.
- Tests: golden SBOMs; license policy unit; E2E with known CVEs; ≥95% coverage.
- Acceptance: deny/unknown enforce; tag `milestone-0.5`.

## Sprint 0.5b — Supply review (Review)
- Validate repeatability and caching; update lessons or rollback.

## Sprint 0.6a — Quality + Reports (Feature)
Goal: style/smell budgets, Prompt Hygiene subgroup, HTML tabs and risk bands.
- Spec: ruff/flake8, eslint mapped; HTML parity.
- Agent: adapters; transformer.
- Tests: adapter unit; HTML snapshots; ≥95% coverage.
- Acceptance: budgets enforce; HTML parity; tag `milestone-0.6`.

## Sprint 0.6b — Quality review (Review)
- Tune noise; update lessons; rollback if UI regresses.

## Sprint 0.7a — Traceability (Feature)
Goal: AC↔tests coverage matrix and diffs.
- Spec: parse `PRIORITY.yaml` IDs; test markers; HTML coverage.
- Agent: parser/resolver; report integration.
- Tests: parser unit; E2E sample repo; ≥95% coverage.
- Acceptance: coverage and diffs in HTML; tag `milestone-0.7`.

## Sprint 0.7b — Traceability review (Review)
- Validate coverage accuracy; add lessons; rollback if mismatch >2%.

## Sprint 0.8a — IDE/Perf/Logging (Feature)
Goal: minimal editor spans, time caps, redacted logs.
- Spec: JSON-span protocol; global/per-pack timeouts; redaction.
- Agent: tasks/extension; timeout enforcement; logging utils.
- Tests: time-cap integration; redaction unit; ≥95% coverage.
- Acceptance: spans shown for ≥2 packs; graceful degradation; tag `milestone-0.8`.

## Sprint 0.8b — IDE/perf review (Review)
- Evaluate UX; update lessons; rollback on instability.

## Sprint 0.9a — Parity/Packaging/IAST null (Feature)
Goal: parity audit, installers, null IAST.
- Spec: parity checklist; container and installers; CLI IAST contract.
- Agent: parity tests; packaging; null provider.
- Tests: matrix; clean-env installs; IAST smoke; ≥95% coverage.
- Acceptance: parity holds; installs ok; IAST callable; tag `v0.9.0`.

## Sprint 0.9b — Final review (Review)
- Full regression; update lessons; release notes; rollback if critical gates fail.
