# ROADMAP — v0.97 “Water Spider” beta → 1.0

Branch: `water-spider` • Tag: `v0.97.0-beta (Water Spider)`

## Milestone M0 — Water-Spider Prep
**Requirements**
- REQ-REL-01: create branch `water-spider`; version scheme v0.97.x; codename appears in release notes.
- REQ-REL-02: pin tool versions (`tools/versions.lock`) for repeatable builds.
- REQ-REL-03: add failing-test decision guide at `.genticode/docs/failing_test_guidelines.md` (from project recipe) and ensure agent reads it before review/reset.
**AC**
- Current branch is `water-spider`.
- Tag template prepared: `v0.97.0-beta (Water Spider)`.
- CI jobs read pinned versions.
- Guide file present and referenced by sprint prompts.

## Milestone M0.6 — Recursion guards + hooks
**Requirements**
- REQ-REC-01: exclude paths from scans/baselines: `.genticode/**`, `ssot/**`, `docs/templates/**`, `images/**`, build/venv, and other generated artifacts.
- REQ-REC-02: `genticode prompt scan` ignores generated outputs and respects `.gitignore`.
- REQ-REC-03: install hooks via `make init`: pre-commit secrets scan; pre-push test-edit guard and waiver check.
**AC**
- Ignore set enforced in CLI and honored in reports.
- Running prompt scan on this repo produces no findings from generated files.
- Hooks install automatically; test deletions/edits without waiver are blocked locally.

## Milestone M1 — SSOT Foundations
**Requirements**
- REQ-SSOT-01: machine-typed SSOT under `ssot/` with JSON Schemas.\
  Files: `ssot/requirements.yaml`, `ssot/decisions.yaml`, `ssot/policy.yaml` (or symlink to `.genticode/policy.yaml`).
- REQ-SSOT-02: deterministic doc render — `genticode docs build` renders `PRD.md`, `ADDH.md`, `docs/changelog.md` from templates.
- REQ-SSOT-03: governance check — `genticode gov check` fails on schema errors, doc drift, or decision-area changes without DEC/REQ reference.
**AC**
- Editing SSOT then running `docs build` is the only path to change PRD/ADDH; direct markdown edits cause CI failure with a clear message.
- Two successive renders are byte-identical.
- `gov check` detects a synthetic gate change without DEC/REQ and fails.

## Milestone M1.6 — Packaging, smoke install, matrix, SBOM
**Requirements**
- REQ-PKG-01: build sdist/wheel and publish to a local index for CI test.
- REQ-PKG-02: `pipx install genticode` smoke test runs `init/check/baseline/report` against a temp repo.
- REQ-PKG-03: pin external tool versions and verify availability; fail with actionable messages.
- REQ-PKG-04: CI matrix on Linux and macOS; Windows explicitly fails fast with guidance (unsupported in beta).
- **REQ-SBOM-01:** Generate SBOMs **from lockfiles only** (CycloneDX). Python: `requirements.txt`+lock or `uv`/`pip-tools`; JS/TS: `package-lock.json` or `pnpm-lock.yaml`.
- **REQ-SBOM-02:** Compare SBOM delta vs previous; gate on license allowlist, `unknown=fail`, and **new high** vulnerabilities.
**AC**
- Smoke install passes on Linux and macOS in CI.
- CLI smoke on a temp repo is green end-to-end.
- Version pins honored; missing tool message shows exact install command.
- **SBOM delta appears in report; merges block on license/unknown/high-vuln violations; no manual SBOM edits permitted.**

## Milestone M2 — Intent Importer + Bootstrap
**Requirements**
- REQ-IMP-01: importer CLI `tools/intent_import.py`.\
  Input: `ssot/bootstrap/intent_feed.jsonl` (types: DEC, REQ, POLICY, NOTE). Validates via JSON Schemas; deep-merges patches; dedupes ACs.\
  Modes: `--dry-run` (diff only), `--apply` (write + `docs build`).
- REQ-IMP-02: complete bootstrap feed of changes since original ADDH.
**AC**
- `--dry-run` prints clean, human-readable diffs for an example feed.
- `--apply` updates SSOT and regenerates docs deterministically.
- Invalid lines abort with precise pointers (line N, path).

## Milestone M2.5 — Prompt Hygiene Bootstrap (explicit)
**Requirements**
- REQ-PROMPT-01: implement prompt scanner for Python and TS/JS; CLI `genticode prompt scan --write-manifest`.
- REQ-PROMPT-02: write manifest `.genticode/prompts.yaml` with entries `{id, version, file, span, hash, purpose}` and a redaction map; deterministic output.
- REQ-PROMPT-03: policy budgets for prompt hygiene (missing id/version/redaction) enforced in gate and visible in report.
**AC**
- Running `genticode prompt scan --write-manifest` creates/updates the manifest deterministically.
- Report shows prompt findings; gate budgets respected.
- Manifest is read during dogfooding initiation and linked in SSOT (reference only).

## Milestone M2.6 — SARIF upload + sample E2E + redaction
**Requirements**
- REQ-SARIF-01: CI job uploads `sarif.json` to PRs; annotations visible.
- REQ-SAMPLE-01: maintain `genticode-sample` repo; run full E2E dogfood on it per PR.
- REQ-RED-01: secrets/log redaction audit — ensure tokens redacted in logs, SARIF, and HTML. Add fake-token fixtures.
**AC**
- SARIF annotations appear on PRs during CI.
- Sample repo E2E run is green and repeatable.
- Redaction tests pass; no secrets leak in artifacts.

## Milestone M3 — TUI v1 (REQ/DEC editor)
**Requirements**
- REQ-TUI-01: VS Code webview TUI hides YAML; edits REQ/DEC via forms (Ajv+RJSF).
- REQ-TUI-02: ID generator, live diff preview, undo, tooltips.
- REQ-TUI-03: save triggers `docs build`; commit scaffold includes DEC/REQ IDs.
- **REQ-TUI-CLI:** Provide CLI fallback: `genticode req new|edit` and `genticode dec new|edit` with the same validations and schemas.
**AC**
- Create and edit a Requirement with ≥1 AC entirely through the TUI; schema violations blocked with inline hints.
- Create and edit a Decision that links to ≥1 REQ; render updated PRD/ADDH with no manual edits.
- Opening YAML directly shows schema hints (yaml-language-server mapping).
- **All REQ/DEC operations possible headlessly via CLI with identical validation.**

## Milestone M4 — Reliability Sprints (pre-beta)
**Requirements**
- REQ-REL-04: migration verification — golden tests for importer (reordered feed → same output), 100% branch coverage on importer.
- REQ-REL-05: governance dry-run — three synthetic PR scenarios: policy change, new pack, schema tweak. Failure messages actionable.
- REQ-REL-06: deterministic CI — seeds, per-test timeout, flake quarantine budget = 0 for beta.
- **REQ-LESSONS-LEDGER:** `LESSONS_ACCEPTED.md` is append-only; CI forbids edits to prior entries; provide compaction tool preserving content and SHA hashes.
**AC**
- Golden tests pass; no nondeterminism detected.
- `gov check` correctly demands DEC/REQ references for the three scenarios.
- CI green twice consecutively on clean clones.
- **Ledger immutability enforced; compaction preserves hashes.**

## Milestone M4.1 — Performance budgets + subprocess audit
**Requirements**
- REQ-PERF-01: per-pack timeouts and a total wall-clock cap; record per-pack timings in report; gate on >2× regression vs baseline.
- REQ-SAFE-01: no `shell=True`; arg allowlists; path confinement to repo root; large-file skips with notices.
**AC**
- Timings appear in report; performance gate functions.
- Safety tests pass: no shell injection, no path escapes, large files handled.

## Milestone M5 — Lessons/Diff Proposals (configurable)
**Requirements**
- REQ-LES-01: propose REQ/DEC drafts from lessons and diffs — `genticode gov propose --from lessons|diff` emits drafts; never mutates SSOT directly.
- REQ-LES-02: configurable unattended mode (default off). Policy keys in `ssot/policy.yaml`:\
  `lessons_ingestion.mode: "draft" | "auto_ready"`\
  `lessons_ingestion.auto_ready_thresholds: { new_classes_pct: 0.6, max_changed_tests: 0, max_attempts_used: 2 }`
- REQ-LES-03: guardrails for unattended mode — auto-ready forbidden if any test edits, deletions, or budget violations exist.
**AC**
- With `mode: draft`, proposals appear as TUI review items and do not change SSOT until confirmed.
- With `mode: auto_ready` and thresholds satisfied, importer creates REQ/DEC entries with `status: ready` and renders docs; otherwise remains draft.
- Attempt logs record the decision path used.

## Milestone M6 — Dogfood Cutover: v0.97.0-beta “Water Spider”
**Requirements**
- REQ-DOG-01: migrate all current intent via importer, review in TUI, regenerate PRD/ADDH.
- REQ-DOG-02: enforce gates on this repo — secrets=0; licenses deny AGPL, unknown=fail; others delta-gated.
- REQ-DOG-03: run prompt scan and load manifest — ensure `.genticode/prompts.yaml` exists and is used by gate/report.
- REQ-DOG-04: traceability and adjudication on — READY ACs must have tests; adjudication records for initial reds; lessons loop active; CODE_FIX path triggers **regeneration**, not manual patching.
- REQ-DOG-05: policy flip audit trail — DEC entry required for phase changes; phase visible in report.
**AC**
- Branch: `water-spider`; tag: `v0.97.0-beta` with “Water Spider” in notes and README badge.
- Every merged PR in decision areas cites DEC+REQ; `gov check` required in CI.
- PRD/ADDH render match SSOT; AC coverage matrix present; SBOMs pass policy.
- Prompt manifest present and enforced; two PRs merged with gates in warn→delta mode, then hard mode enabled without regressions.
- Phase changes recorded as DEC and rendered in report.
