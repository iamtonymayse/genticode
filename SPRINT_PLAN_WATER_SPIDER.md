# SPRINT_PLAN_WATER_SPIDER.md — to v0.97 “Water Spider” beta

## Global conventions

- Tag before any Feature sprint: `git tag pre-<sprint-id>`.
- Run the **entire** test suite once per attempt with timeouts. Collect all failures.
- Adjudicate using `.genticode/docs/failing_test_guidelines.md`. Generate decision records for each failing test.
- **Regeneration-only rule:** If any tests fail, write lessons, **reset to pre-tag**, and regenerate code with improved prompts. Do not patch product code to make tests pass. Test edits require a waiver + requirement evidence. Never delete tests.
- Attempts: max 3. Allow a 4th only if >50% failures are **new classes**. If still red, split scope.
- Coverage: ≥95% for changed code. Per-test timeout default 30s. Suite cap default 20m local / 30m CI.
- Seeds and versions: record seeds, env, and tool versions in attempt logs; use `tools/versions.lock`.

## Agent preface (use before every Feature sprint)

> Read: `ROADMAP_WATER_SPIDER.md`, this file, `.genticode/docs/failing_test_guidelines.md`, and `.genticode/local/LESSONS_CURRENT.md` (if present). Obey the regeneration-only rule. Create minimal plausible implementations with high test coverage. Prefer small, composable functions. On first red after a full run, stop, adjudicate, write lessons, reset, and regenerate guided by lessons. Never nerf tests.

---

## S0a — Prep (branch, pins, guide) — Effort: 0.5–1h, Thinking: Low, P≥0.99

**Spec**
- Create branch `water-spider`.
- Add `tools/versions.lock` with exact versions for Python, semgrep, cyclonedx, pytest plugins, node, npm.
- Add `.genticode/docs/failing_test_guidelines.md` (from provided project recipe).

**Checklist**
- `git checkout -b water-spider`.
- Write `tools/versions.lock` with example contents and comments.
- Place failing-test guide and link it in README and this plan.

**AC**
- Branch exists; versions file loaded by CI; guide present and referenced.

---

## S0b — Review S0a — Effort: 0.25h, Thinking: Low, P≥0.99
Run full tests; if red → lessons → reset → regenerate; else accept and copy lessons (if any) to accepted ledger.

---

## S0.6a — Recursion guards + hooks — Effort: 2–3h, Thinking: Medium, P≥0.96

**Spec**
- Add ignore set to CLI scanners and baseline: `.genticode/**`, `ssot/**`, `docs/templates/**`, `images/**`, `dist/**`, `build/**`, `.venv/**`, `node_modules/**`, generated reports.
- Ensure `genticode prompt scan` respects `.gitignore`.
- Install hooks via `make init`: pre-commit secrets scan, pre-push test-edit guard + waiver check.

**Functional details**
- Implement `genticode/common/ignore.py` exposing `DEFAULT_IGNORES` and `should_ignore(path: Path, repo_root: Path) -> bool`.
- Update all pack runners to call `should_ignore` and to confine paths under repo.
- Hook installer adds `.git/hooks/pre-commit` and `.git/hooks/pre-push` from `scripts/hooks/*`.

**AC**
- Running prompt scan yields no findings from generated paths.
- Test deletions/edits without waiver are blocked locally.
- Reports and baselines exclude ignored paths.

---

## S0.6b — Review S0.6a — Effort: 0.25h, Thinking: Low, P≥0.99
Test hook behavior with staged changes; confirm ignores via dry runs.

---

## S1a — SSOT foundations — Effort: 4–5h, Thinking: Medium, P≥0.96

**Spec**
- Create SSOT files: `ssot/requirements.yaml`, `ssot/decisions.yaml`, `ssot/policy.yaml` (or symlink from `.genticode/policy.yaml`).
- Implement `genticode docs build` to render `PRD.md`, `ADDH.md`, `docs/changelog.md` using deterministic Jinja templates.
- Implement `genticode gov check` to validate schemas, detect markdown drift, and require DEC/REQ references on decision-area diffs.

**Schemas (concise)**

`schema/requirements.schema.json`:
```json
{
  "$id":"req.schema.json",
  "type":"array",
  "items":{
    "type":"object",
    "required":["id","title","status","acceptance"],
    "properties":{
      "id":{"type":"string","pattern":"^REQ-[A-Z0-9-]+$"},
      "title":{"type":"string","minLength":3},
      "status":{"enum":["ready","in_progress","done"]},
      "non_functional":{"type":"object","additionalProperties":true},
      "acceptance":{
        "type":"array",
        "items":{
          "type":"object",
          "required":["id","text"],
          "properties":{
            "id":{"type":"string","pattern":"^AC-[A-Z0-9-]+$"},
            "text":{"type":"string"},
            "coverage":{"enum":["required","optional"]}
          }
        }
      }
    }
  }
}
```

`schema/decisions.schema.json`:
```json
{
  "$id":"dec.schema.json",
  "type":"array",
  "items":{
    "type":"object",
    "required":["id","context","decision","status"],
    "properties":{
      "id":{"type":"string","pattern":"^DEC-[0-9]{4}-[0-9]{2}-.+$"},
      "context":{"type":"string"},
      "decision":{"type":"string"},
      "consequences":{"type":"string"},
      "status":{"enum":["draft","accepted","reversed","superseded"]},
      "links":{"type":"object","properties":{"req":{"type":"array","items":{"type":"string"}},"prs":{"type":"array","items":{"type":"string"}},"lessons":{"type":"array","items":{"type":"string"}}}}
    }
  }
}
```

**AC**
- Deterministic renders; drift detection works; missing DEC/REQ reference on a synthetic change fails `gov check` with actionable message.

---

## S1b — Review S1a — Effort: 0.5h, Thinking: Low, P≥0.99
Run tests and docs twice; ensure byte-identical output; apply lessons if needed and regenerate.

---

## S1.6a — Packaging, smoke install, matrix, SBOM — Effort: 3–4h, Thinking: Medium, P≥0.96

**Spec**
- Add `pyproject.toml` with build backend, console scripts.
- CI builds sdist/wheel, matrix Linux/macOS, performs `pipx install genticode` smoke run on a temp repo.
- Verify external tools per `tools/versions.lock`, fail with clear messages when missing.
- **SBOM provenance and delta gate:**
  - Generate SBOMs from lockfiles only (CycloneDX).
  - Compare against previous SBOM; gate on license allowlist, `unknown=fail`, and **new high** vulnerabilities.
  - Render SBOM delta summary into report.

**AC**
- `pipx install` works in CI; `genticode init/check/baseline/report` passes on temp repo.
- Version pins honored; missing tool message includes install instructions.
- **SBOM delta visible; merges block on license/unknown/high-vuln violations; no manual SBOM edits.**

---

## S1.6b — Review S1.6a — Effort: 0.25h, Thinking: Low, P≥0.99
Confirm smoke pipeline and SBOM gates; record lessons; regenerate as needed.

---

## S2a — Intent importer — Effort: 3–4h, Thinking: Medium, P≥0.96

**Spec**
- Build `tools/intent_import.py` with JSONL feed support (`DEC`, `REQ`, `POLICY`, `NOTE`), `--dry-run` and `--apply`.
- Validate with pydantic or jsonschema; deep-merge policy patches; dedupe ACs; stable sort keys.

**AC**
- `--dry-run` produces human-readable diffs. `--apply` updates SSOT and regenerates docs deterministically. Invalid lines pinpointed.

---

## S2b — Review S2a — Effort: 0.5h, Thinking: Low, P≥0.99
Run valid/invalid feeds; confirm behavior; lessons → reset → regenerate if needed.

---

## S2.5a — Prompt hygiene bootstrap — Effort: 3–4h, Thinking: Medium, P≥0.96

**Spec**
- Implement `genticode prompt scan --write-manifest` for Python and TS/JS.
- Manifest `.genticode/prompts.yaml` entries: `{ id, version, file, start_line, end_line, hash, purpose, redaction: {strategy, samples} }`.
- Add policy budgets and report section.

**AC**
- Deterministic manifest; report shows prompt findings; gate budgets respected.

---

## S2.5b — Review S2.5a — Effort: 0.25h, Thinking: Low, P≥0.99
Run scan twice; identical outputs; red → lessons → reset → regenerate if needed.

---

## S2.6a — SARIF upload + sample E2E + redaction — Effort: 2–3h, Thinking: Medium, P≥0.96

**Spec**
- CI step uploads `sarif.json` annotations to PRs.
- Maintain `genticode-sample`; run end-to-end check on it per PR.
- Add fixtures with fake tokens; assert redaction across logs, SARIF, HTML.

**AC**
- PR shows SARIF annotations; sample repo green; redaction tests pass.

---

## S2.6b — Review S2.6a — Effort: 0.25h, Thinking: Low, P≥0.99
Confirm annotations and E2E; lessons → reset → regenerate if needed.

---

## S3a — TUI v1 (REQ/DEC) — Effort: 5–6h, Thinking: Medium, P≥0.95

**Spec**
- VS Code webview extension:
  - Tree view for Requirements and Decisions.
  - Forms via RJSF + Ajv validation.
  - ID generator, tooltips, live diff preview, undo.
  - Save: writes SSOT and runs `genticode docs build`; shows doc diff.
  - YAML schemas surfaced to yaml-language-server.
- **CLI fallback:** implement `genticode req new|edit` and `genticode dec new|edit` (same schema validations).

**AC**
- Create/edit REQ with ≥1 AC; create/edit DEC linked to REQ; docs regenerate; no manual YAML edits.
- **Headless CLI flow performs the same operations with identical validation.**

---

## S3b — Review S3a — Effort: 0.5h, Thinking: Low, P≥0.99
Exercise end-to-end; apply lessons/reset/regenerate if red.

---

## S4a — Reliability sprints — Effort: 3h, Thinking: Medium, P≥0.96

**Spec**
- Golden tests for importer (order-insensitive). 100% branch coverage.
- Governance dry-run: simulate policy change, new pack, schema tweak; verify `gov check` failures are actionable.
- Deterministic CI: seeds, per-test timeouts, quarantine budget = 0.
- **Lessons ledger hygiene:** `LESSONS_ACCEPTED.md` append-only; CI check prevents edits; compaction tool preserves content and SHA hashes.

**AC**
- Golden tests pass; dry-run failures informative; CI green twice on clean clones.
- **Ledger immutability enforced; compaction preserves hashes.**

---

## S4b — Review S4a — Effort: 0.25h, Thinking: Low, P≥0.99
Confirm determinism, lessons loop if needed.

---

## S4.1a — Performance budgets + subprocess audit — Effort: 3h, Thinking: Medium, P≥0.96

**Spec**
- Record per-pack timings; persist baseline; gate on >2× regression.
- Enforce safety: no `shell=True`; arg allowlists; repo-root path confinement; large-file skip with notice.

**AC**
- Timings visible in report; regression gate works; safety tests pass.

---

## S4.1b — Review S4.1a — Effort: 0.25h, Thinking: Low, P≥0.99
Run timing regression scenario; confirm gate and safety.

---

## S5a — Lessons/Diff proposals (configurable) — Effort: 3h, Thinking: Medium, P≥0.96

**Spec**
- `genticode gov propose --from lessons|diff` produces REQ/DEC **drafts**.
- Config in `ssot/policy.yaml`:
```yaml
lessons_ingestion:
  mode: draft          # or auto_ready
  auto_ready_thresholds:
    new_classes_pct: 0.6
    max_changed_tests: 0
    max_attempts_used: 2
```
- Guardrails: auto_ready forbidden if test edits/deletions/budget violations present.

**AC**
- Draft proposals appear in TUI and are editable. Auto-ready only when thresholds met; decision path logged.

---

## S5b — Review S5a — Effort: 0.25h, Thinking: Low, P≥0.99
Test both modes; ensure guardrails deny unsafe auto-ready.

---

## S6a — Dogfood cutover — v0.97.0-beta “Water Spider” — Effort: 3–4h, Thinking: Medium, P≥0.96

**Spec**
- Run importer on `ssot/bootstrap/intent_feed.jsonl`; review in TUI; regenerate PRD/ADDH.
- Enable gates: secrets=0, licenses deny AGPL/unknown=fail; others delta.
- Run prompt scan; ensure `.genticode/prompts.yaml` loaded by gate/report.
- Turn on traceability and adjudication; apply regeneration-only rule for product code when tests fail.
- Tag beta and update README badge.

**AC**
- Tag `v0.97.0-beta (Water Spider)`; PRs show DEC+REQ; AC matrix present; SBOMs and prompt gates pass.
- Two PRs merged with warn→delta, then move to hard with DEC audit trail.

---

## S6b — Review S6a — Effort: 0.5h, Thinking: Low, P≥0.99
Flip remaining gates to hard; confirm stability; copy accepted lessons to ledger.

---

### Review sprint protocol (applies to every Review sprint)

1) Run full test suite with timeouts. Collect **all** failures in one run.
2) Use `.genticode/docs/failing_test_guidelines.md` to classify each failure; generate decision records.
3) If any failures: write 5‑Whys lessons; **reset to pre-tag**; **regenerate** code with updated prompts; rerun.
4) Only update tests with waiver + requirement evidence; never delete tests.
5) If still failing after max attempts, split scope for next sprint.
