# ROADMAP_BATCHING_ORDERING.md
**Release:** v0.9.x (minor)  
**Theme:** Deterministic batching & ordering for fast, predictable runs

## Objective
Introduce first-class batching and ordering policies across scan → normalize → compare → report, with deterministic artifacts and CI-enforceable behavior.

## Why now
- Shrinks wall-clock time without degrading safety (parallel + fairness).
- Eliminates “heisen-failures” from nondeterministic task order.
- Unblocks nightly jobs and multi-repo adoption.

## Scope (MVP)
1. **CLI**
   - `--batch {auto,n,by-tool,by-path}`
   - `--order {deterministic,topo,required-first,risk-first}`
   - `--max-duration`, `--per-task-timeout`, `--parallel {N|auto}` (reuse existing flags where present).
2. **Engine**
   - Stable task graph with content-addressed IDs.
   - Batch scheduler (size caps, backpressure, fairness).
   - Deterministic seed & tie-breakers (path, hash, index).
3. **Artifacts**
   - `artifacts/run.json` carries `batch_id`, `order_policy`, `seed`, `graph_hash`.
   - JSONL task log with per-batch timing & exit status.
4. **CI gates**
   - Fail on policy drift (order policy mismatch).
   - Enforce deterministic compare (no unordered keys; stable lists).
5. **Docs**
   - “How to pick a policy” playbook with examples.
   - Migration notes: defaults, compatibility, env overrides.

## Non-Goals
- Global cost-aware scheduling.
- Cross-repo orchestration.
- Dynamic reprioritization during a run.

## Deliverables
- `genti run` supports new flags.
- Deterministic order by default (`deterministic` policy).
- Batch scheduler with fairness + time caps.
- Golden tests: same inputs → same outputs, bytewise (except timestamps).
- CI workflow update + docs.

## Acceptance Criteria
- Two identical runs (cold cache) produce identical `report.json`, `run.json`, and task logs.
- Parallelism ≠ order variance (proven by golden).
- CI fails when policy differs from repo default.
- E2E: `scan → normalize → compare` completes under time caps with `--parallel auto` and `--batch auto` on a representative repo.

## Milestones
- **M1**: CLI & policy plumbing + deterministic iterator (1–2d)
- **M2**: Batch scheduler & fairness (2–3d)
- **M3**: Artifacts + golden tests (1–2d)
- **M4**: CI + docs + migration guide (1–2d)

## Risks & Mitigations
- Flaky “determinism”: add seed, sort keys, stable tiebreakers.
- Regressed throughput: benchmark; expose `--batch n` escape hatch.
- Hidden OS/fs ordering: normalize via in-memory sorted enumerations.

## Tracking
- Epic: `BATCH-ORDER-EPIC`
- Tags: `perf.parallelism`, `cli.surface`, `ci.gates`, `report.formats`