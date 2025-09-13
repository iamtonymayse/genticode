# SPRINT_PLAN.md — Multi‑Pass Lessons Loop (v0.9.x)

Intent
- Allow multiple full‑suite attempts per Feature sprint before splitting scope.
- Prevent reward hacking: tests are immutable unless a waiver with evidence.
- Keep success probability ≥95% by capping attempts and time.

## Policy: Fail‑After‑Full‑Run with Multi‑Pass Retries
- Run the **entire** test suite once per attempt with hard timeouts.
- Collect **all** failures, batch diagnosis, write lessons, then reset and retry.
- Default cap: **max_attempts = 3** per Feature sprint.
- Permit a **4th attempt** only if >50% of failures are **new classes** (not seen before).
- If failures persist after the cap, **split the sprint** along failure classes and proceed.

### Heuristics to split vs retry
- **Retry** if: failures map to ≤2 classes and lessons are actionable (requirements clarified, missing checks, clear API misuse).
- **Split** if: same class appears after 2 attempts, or failures span ≥3 unrelated classes, or ETA exceeds 6 agent‑hours.

## Attempt mechanics
- Per‑test timeout: 30s (configurable).
- Suite cap per attempt: 20m local; 30m CI.
- Attempt log: `.genticode/local/attempts/attempt-<n>.json` with failures grouped by class.
- Lessons files: `.genticode/local/LESSONS.md` → merge → `LESSONS_CURRENT.md`, copy applied to `LESSONS_ACCEPTED.md` on acceptance.

---

## Sprint 0.9L1a — Implement Multi‑Pass Loop (Feature)
**Goal:** Encode attempts, logs, decisions, and guardrails.

### Functional spec
1. **Attempt runner** script: `scripts/attempt.py`
   - Runs `pytest` with: `--maxfail=0 --timeout=30 --json-report --json-report-file=.genticode/raw/pytest.json --cov --cov-branch --cov-fail-under=95`.
   - Parses report, groups failures: {Requirements|Design|Code|Test|Tooling|Env}.
   - Writes `.genticode/local/attempts/attempt-<n>.json` with summary.
2. **Decision helper**: `scripts/lessons_decide.py`
   - Input: last two attempts’ JSON.
   - Output: `RETRY` or `SPLIT` with rationale; percentage of new failure classes.
3. **Reset protocol**
   - If any failures: write/merge lessons, then `git reset --hard pre-<sprint-id>`.
4. **Guardrails for tests**
   - Pre‑push hook or `scripts/guard.sh` blocks test deletions and edits without waiver under `.genticode/local/waivers/*.yaml` (approved:true).

### Checklist
- `scripts/attempt.py` creates attempt logs and a concise summary markdown at `.genticode/reports/attempt-<n>.md`.
- `scripts/lessons_decide.py` reports decision and rationale.
- Update `AGENTS.md` with multi‑pass loop, caps, and commands.
- Update `SPRINT_PLAN.md` references to use attempts flow.

### Acceptance criteria
- One Feature sprint can run up to 3 attempts automatically: run → diagnose → lessons → reset → retry.
- 4th attempt only allowed when new classes >50% (decision helper confirms).
- Test edits blocked without waiver; deletions always blocked.
- Coverage ≥95% enforced per attempt.
- All new scripts have unit tests (≥95% coverage).

**Effort:** 3–4 agent‑hours, 0.5 human‑hours. **Thinking:** Medium. **Success P:** ≥0.96.

---

## Sprint 0.9L1b — Review 0.9L1a (Review/Reset)
- Run two seeded failure scenarios; verify attempt logs and correct decisions (RETRY then SPLIT).
- Ensure lessons merge (CURRENT, ACCEPTED) and reset behavior.
- If anything fails, add lessons, reset to `pre-0.9L1a`, retry.

**Effort:** 0.5 agent‑hours. **Thinking:** Low. **Success P:** 0.99.

---

## Sprint 0.9L2a — Integrate Loop into Active Sprints (Feature)
**Goal:** Embed multi‑pass in all feature sprints with minimal friction.

### Functional spec
- Patch all Feature sprint “Stop rules” to:
  1) Run `scripts/attempt.py` (attempt 1).
  2) If red: write lessons, reset, attempt 2.
  3) If still red: write lessons, reset, attempt 3.
  4) If still red: run `scripts/lessons_decide.py` → if RETRY and allowed (new classes >50%), attempt 4; else split scope per classes.
- Add per‑sprint **Time budget**: ≤6 agent‑hours total, ≤30m CI runtime per attempt.

### Checklist
- Update each sprint section with “Attempts” bullet list.
- Add “Split plan” note on how to carve scope by failure classes.

### Acceptance criteria
- Dry‑run plan through two existing sprints; produce mock attempt logs and decisions.
- CI workflow cap respected; suite timeouts enforced.
- Documentation aligned: `README.md` Lessons Loop section references attempts and split heuristic.

**Effort:** 2–3 agent‑hours. **Thinking:** Medium. **Success P:** ≥0.96.

---

## Sprint 0.9L2b — Review 0.9L2a (Review/Reset)
- Validate with one synthetic repo: ensure max_attempts=3 default, optional 4th with qualifier, then enforce split.
- Confirm waivers required for any test edits; deletions blocked.
- Lessons accepted ledger updated.

**Effort:** 0.5 agent‑hours. **Thinking:** Low. **Success P:** 0.99.

---

## Commands

Full attempt run (local):
```bash
CAP=1200 scripts/run pytest -q --maxfail=0 --disable-warnings   --timeout=30 --cov --cov-branch --cov-fail-under=95   --json-report --json-report-file=.genticode/raw/pytest.json
python scripts/attempt.py  # writes attempt-N.json and attempt-N.md
```

Reset and retry:
```bash
git reset --hard pre-<sprint-id>
# re‑implement per LESSONS_CURRENT.md, then:
python scripts/attempt.py
```

Decision helper:
```bash
python scripts/lessons_decide.py --prev .genticode/local/attempts/attempt-2.json   --curr .genticode/local/attempts/attempt-3.json
# outputs: RETRY or SPLIT + rationale
```

---

## Test‑edit waiver (git‑ignored)
`.genticode/local/waivers/test-change-YYYYMMDD-<sprint>.yaml`:
```yaml
approved: true
sprint: <id>
reason: "<why the test was wrong>"
evidence: "<link to AC/spec proving mismatch>"
scope: ["tests/path_or_file"]
expires: "<YYYY-MM-DD>"
owner: "<name>"
```

---

## Thinking and success table

| Sprint | Thinking | Agent‑hours | Success P(≥) |
|---|---|---:|---:|
| 0.9L1a Multi‑pass loop | Medium | 3–4 | 0.96 |
| 0.9L1b Review | Low | 0.5 | 0.99 |
| 0.9L2a Integrate in sprints | Medium | 2–3 | 0.96 |
| 0.9L2b Review | Low | 0.5 | 0.99 |

---

## Notes
- Keep attempts deterministic: record seeds, env, tool versions in attempt‑N.md.
- Never change tests to make green without a waiver and evidence.
- If split is chosen, open follow‑up sprints per failure class and carry forward `LESSONS_CURRENT.md`.
