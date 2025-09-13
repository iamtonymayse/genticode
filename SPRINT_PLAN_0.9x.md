# SPRINT_PLAN — v0.9.x with Explicit Review/Reset

Conventions
- Before each Feature sprint: tag `pre-<id>`, branch `feat/<id>`.
- After each Feature sprint: run the paired Review sprint. Decide reset or accept.
- Lessons files (git‑ignored): `.genticode/local/LESSONS.md`, `LESSONS_CURRENT.md`, `LESSONS_ACCEPTED.md`.

Thinking and success
- Feature sprints: Medium thinking, ≤6 agent‑hours, ≥95% success target.
- Review sprints: Low thinking, ≤1 agent‑hour, aim 100% success.

---

## 0.9.1a — Policy Engine (Feature)
Spec
- Implement `policy.py`: `PolicyConfig`, `PackConfig`, `load(path)`, `severity_map`, `get_budget(pack, severity)`, `get_phase()`.
- Validate YAML against an internal schema; helpful errors.

Checklist
- Parse `.genticode/policy.yaml`.
- Remove hardcoded budgets in CLI/gate.
- Unit tests for invalid/valid examples.

AC
- Editing `policy.yaml` changes `genticode check` behavior with no code edits.
- All tests ≥95% coverage in policy module.

## 0.9.1b — Review 0.9.1a (Review/Reset)
- Re‑run tests. If any fail → add lessons to `LESSONS.md`, merge to `LESSONS_CURRENT.md` (supersede older). Reset with `git reset --hard pre-0.9.1a` and retry.
- If pass and lessons applied → copy accepted items to `LESSONS_ACCEPTED.md` under this sprint.

---

## 0.9.1c — Progressive Enforcement (Feature)
Spec
- Gate phases: `warn | new_code_only | hard`. Compute “new code” from baseline + diff.
- Exit codes: 0 pass, 1 warn, 2 fail.

Checklist
- Implement phase selection via policy.
- Unit + E2E cases for each phase.

AC
- Phase toggles produce expected exit codes across seeded cases.

## 0.9.1d — Review 0.9.1c (Review/Reset)
- Same review protocol. Reset if AC missed.

---

## 0.9.1e — Baseline/Delta for All Packs (Feature)
Spec
- Generalize baseline schema; deltas for Prompt, Static, Supply, Quality, Traceability.
- Suppressions with `{id, owner, reason, expires}`.

Checklist
- Snapshot/compare per pack.
- Suppression expiry honored.

AC
- Gate evaluates deltas across all packs; suppressions work; tests ≥95%.

## 0.9.1f — Review 0.9.1e (Review/Reset)

---

## 0.9.1g — Unified SARIF (Feature)
Spec
- Transform normalized findings from all packs to SARIF with rules, locations, fix suggestions.

Checklist
- Golden SARIF fixtures.
- GitHub annotation smoke on sample repo (local run).

AC
- `sarif.json` includes all findings with correct severities and spans.

## 0.9.1h — Review 0.9.1g + Release 0.9.1 (Review/Reset)

---

## 0.9.2a — Orchestrator + Pack Interface (Feature)
Spec
- `orchestrator.py`: coordinates packs, timeouts, errors.
- `Pack` ABC: `run(root, cfg) -> Raw`, `normalize(raw) -> Findings`.

Checklist
- CLI delegates to orchestrator.
- Fault‑injection tests with fake packs.

AC
- Packs pluggable; CLI <-> orchestrator boundary covered by tests.

## 0.9.2b — Review 0.9.2a (Review/Reset)

---

## 0.9.2c — Static Completion (Feature)
Spec
- Add secrets/PII detectors; complete normalization; configurable rulesets in policy.

Checklist
- Secrets patterns and tests.
- PII heuristics behind policy flags.

AC
- Secrets/PII findings present; ruleset switchable; ≥95% coverage.

## 0.9.2d — Review 0.9.2c (Review/Reset)

---

## 0.9.3a — Supply Vuln Import (Feature)
Spec
- Import pip‑audit and npm/OSV. De‑dupe; add fix hints. Enforce license budgets.

Checklist
- SBOM → vuln map.
- License allow/deny + unknown per policy.

AC
- Deny/unknown enforced; vuln findings normalized with fixes.

## 0.9.3b — Review 0.9.3a (Review/Reset)

---

## 0.9.3c — Quality + Flake Detector (Feature)
Spec
- ruff/flake8 + eslint mapped to severities.
- Flake detector: N re‑runs, rate window, budgets.

Checklist
- Flake simulator tests.
- HTML shows Quality metrics.

AC
- Flake rate reported and budgeted; linters feed normalized findings.

## 0.9.3d — Review 0.9.3c (Review/Reset)

---

## 0.9.4a — Traceability (Feature)
Spec
- Parse `PRIORITY.yaml` AC IDs; test markers; coverage matrix + diffs; optional budget on missing coverage.

Checklist
- Parser/resolver with examples.
- HTML coverage matrix.

AC
- AC coverage visible; budget toggles fail if configured.

## 0.9.4b — Review 0.9.4a (Review/Reset)

---

## 0.9.4c — Hardening, Concurrency, Docs (Feature)
Spec
- Subprocess safety, path/size limits, process‑pool parallelism, per‑pack timeouts, better errors.
- Integration tests; policy examples doc.

Checklist
- No `shell=True`; input validation.
- Large‑file skip + notice.
- Parallel pack runner.

AC
- Packs run in parallel with caps; integration tests pass; docs include runnable policy snippets.

## 0.9.4d — Final Review 0.9.4c + Release 0.9.4 (Review/Reset)

---

## Review Sprint Protocol (explicit)
At each Review sprint:
1) Re‑run `make test` and any `genticode check` cases. Run `scripts/guard.sh`.
2) If anything fails: add lesson entries to `.genticode/local/LESSONS.md` using the template. Merge into `LESSONS_CURRENT.md` by superseding older items.
3) If the Feature sprint is accepted and lessons were applied: copy those entries to `LESSONS_ACCEPTED.md` under this sprint.
4) Decide:
   - **Reset:** `git reset --hard pre-<id>` then retry the Feature sprint applying `LESSONS_CURRENT.md`.
   - **Advance:** proceed to next sprint and keep lessons on file.
