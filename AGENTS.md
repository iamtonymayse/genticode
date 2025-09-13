# AGENTS.md — Genticode v0.9 Development on macOS (Codex, GPT‑5 Thinking)

Purpose: enable an autonomous Codex agent to deliver Genticode from 0.1 → 0.9 with minimal human input. This guide binds the ADDH, PRD, ROADMAP, and SPRINT plan into an executable runbook.

Read first each sprint:
1) `PRD.md`, `ROADMAP.md`, `SPRINT_PLAN.md`.
2) `.genticode/local/LESSONS_CURRENT.md` if present.
3) This file.

---

## 1. Guardrails and Principles
- **Scope discipline:** Work only on the active sprint from `SPRINT_PLAN.md`.
- **One run, one report, one gate:** converge outputs to `.genticode/report.json`; derive `sarif.json` and `report.html` from it.
- **MPI:** implement the minimal plausible functionality to pass acceptance criteria.
- **Coverage:** keep ≥95% for sprint-owned code.
- **Determinism:** record seeds and environment; prefer pinned tool versions.
- **Local-first:** never exfiltrate secrets or write outside repo root.
- **Timeouts:** wrap blocking commands with a 120s default cap, 600s for long ops.
- **Idempotence:** steps must be re-runnable without manual cleanup.
- **Stop rule:** if acceptance criteria pass, stop; else create remediation notes and proceed to Review sprint workflow.

---

## 2. macOS Environment (with coreutils)
Assumptions: macOS 12+, Homebrew available.

```bash
brew update
brew install coreutils gnu-sed gawk jq yq git python@3.11 node@20 semgrep fd ripgrep
python3.11 -m pip install --upgrade pip pipx
pipx ensurepath
python3.11 -m venv .venv && source .venv/bin/activate
```

Notes
- Supported minima: Python 3.10+, Node 18+. macOS installs above are acceptable.
- Detect `gtimeout` at `/opt/homebrew/bin/gtimeout` or `/usr/local/bin/gtimeout`.
- Prefer `jq`, `yq`, `rg`, `fd` in scripts.

Project bootstrap
```bash
mkdir -p .genticode/{logs,cache,raw,reports,baseline,candidates} .genticode/local
echo ".genticode/local/" >> .gitignore  # ensure lessons remain untracked
```

---

## 3. Files to Honor
- **Specs:** `ADDH.md`, `PRD.md`, `ROADMAP.md`, `SPRINT_PLAN.md`.
- **Lessons:** `.genticode/local/LESSONS_CURRENT.md` (active), `LESSONS.md` (scratch), `LESSONS_ACCEPTED.md` (audit).
- **Artifacts:** `.genticode/report.json`, `sarif.json`, `report.html`, `baseline/*`, `raw/*`, `cache/*`, `candidates/*`.
- **Evidence:** `.genticode/reports/AC_<sprint>.md` and JSON test outputs in `.genticode/raw/`.

---

## 4. Sprint Execution Loop

### 4.1 Sprint Contract (create at start)
Create `.genticode/logs/sprint_contract.yaml`:
```yaml
sprint: <id>                 # e.g., 0.3a
goals:                       # short bullet list from SPRINT_PLAN
acceptance:                  # copy exact ACs
risks:                       # guessed risks → mitigations
timeouts: {default: 120, long: 600}
seeds:   {builder: [42, 31415, 27182]}
thinking: low|medium         # from SPRINT_PLAN table
artifacts: [.genticode/report.json, .genticode/report.html, .genticode/sarif.json]
```

Create a branch `feat/<sprint-id>` and a tag `pre-<sprint-id>`.

### 4.2 Parallel Proposal Mode (PPM)
Run 2–3 builder attempts with different seeds. Each builder:
1) Reads Sprint Contract and Lessons Current.
2) Implements within scope only.
3) Produces a candidate bundle in `.genticode/candidates/A<index>/`:
```
diff.patch
notes.md
raw/pytest.json
raw/semgrep.json
report.json (if applicable)
```

### 4.3 Selection and Merge
Score candidates:
- All ACs satisfied, tests pass, coverage ≥95%, smaller diff, fewer deps, faster runtime.
Merge best, cherry-pick micro-fixes if strictly in scope.

### 4.4 Evidence and Commit
Write `.genticode/reports/AC_<sprint-id>.md` with:
- AC checklist ✅/❌
- Test summary, coverage, timings, seeds, env
- Links to artifacts

Commit with message:
```
feat(<sprint-id>): <one-line>
AC: <list>
Evidence: .genticode/reports/AC_<sprint-id>.md
```

If this closes a milestone, tag `milestone-<M>`.

---

## 5. Review Sprint Workflow

1) Re-run full tests and gates.
2) If any fail, capture lessons in `.genticode/local/LESSONS.md` using the template below.
3) **Merge and supersede:** produce `.genticode/local/LESSONS_CURRENT.md` by merging new lessons with prior current, marking superseded items.
4) If the Feature sprint is approved and lessons were applied, append those entries to `.genticode/local/LESSONS_ACCEPTED.md` under a new heading for the sprint.
5) Decide rollback:
   - If ACs unmet or gates failed: `git reset --hard pre-<sprint-id>` and retry the Feature sprint with updated lessons.
   - Else proceed to the next sprint.

Lesson entry template (YAML):
```yaml
id: LES-YYYYMMDD-<sprint-id>-<slug>
sprint: <sprint-id>
date: YYYY-MM-DD
status: proposed|accepted|superseded
category: Requirements|Design|Code|Test|Tooling|Environment|Process
trigger: <what failed and where>
failing_signal: <test name|gate|log excerpt>
root_cause: |
  why1
  why2
  why3
improved_instructions:
  - <imperative checklist item>
preventive_controls:
  - <test/rule/budget to add>
supersedes: [<lesson-ids>]
notes: <links or short context>
```

Root-cause method:
- Classify defect, apply 5 Whys (3–5 lines), attach failing test or gate, propose improved instructions and preventive controls, mark superseded items.

---

## 6. Thinking Level and Sizing
Choose thinking based on the SPRINT plan table:
- **Low:** straightforward wiring or shell; expected success ≥99%.
- **Medium:** adapter integration or normalization; expected success ≥95%.
Rules:
- Keep a Feature sprint under ~6 agent-hours.
- If scope exceeds that, split tasks or carry forward to next sprint.
- Always prefer MPI; defer non-essential features.

---

## 7. Genticode-Specific Runbooks

### 7.1 Report pipeline
- Always write `.genticode/report.json` first.
- Derive `sarif.json` and `report.html` from that JSON.
- Validate JSON schema via tests; snapshot HTML.

### 7.2 Prompt Hygiene
- Detect prompt-like strings in Python and TS/JS.
- Maintain `.genticode/prompts.manifest.json` with IDs and hashes.
- Enforce lints: missing IDs/versions, secret placeholders, oversize URLs.
- Provide safe autofixes: constant extraction and redaction.

### 7.3 Static pack
- Run Semgrep for Python and TS/JS with curated rules.
- Normalize to unified severities and dedupe overlaps.
- Cache rulepacks under `.genticode/cache/`.

### 7.4 Baseline and Gates
- Implement `baseline capture|clear`.
- Gate on budgets with phases: warn → new_code_only → hard.
- Exit codes: 0 pass, 1 warn, 2 fail.

### 7.5 Supply pack
- Generate CycloneDX SBOMs for pip/poetry and npm/yarn.
- Import vulnerabilities; enforce license allow/deny and unknown-fail.

### 7.6 Quality pack and Reports
- Integrate ruff/flake8 and eslint; map to severities.
- Enhance HTML with tabs, risk bands, and deltas.

### 7.7 Traceability
- Parse `PRIORITY.yaml` AC IDs and test markers.
- Emit coverage matrix and diffs since baseline.

### 7.8 IDE, perf, logging
- Emit spans for VS Code tasks/extension.
- Enforce global/per-pack timeouts.
- Redact logs by default; opt-in debug verbosity.

---

## 8. Standard Commands (with time caps)

Wrapper:
```bash
GTO=$(command -v gtimeout || true); CAP=${CAP:-120}
if [ -n "$GTO" ]; then "$GTO" ${CAP}s bash -lc "$*"; else python - <<PY
import subprocess,sys
try: subprocess.run(sys.argv[1],shell=True,timeout=int(sys.argv[2]),check=True)
except subprocess.TimeoutExpired: print("TIMEOUT",file=sys.stderr); exit(124)
PY
fi
```

Examples:
```bash
# tests
CAP=600 ./run "pytest -q --maxfail=1 --disable-warnings --cov --cov-branch --cov-fail-under=95   --json-report --json-report-file=.genticode/raw/pytest.json"

# semgrep
./run "semgrep --error --config p/python --config p/typescript --json --timeout=120   | tee .genticode/raw/semgrep.json >/dev/null"

# sbom (python)
./run "cyclonedx-py -o .genticode/raw/sbom-python.json || true"

# sbom (node)
./run "npx @cyclonedx/cyclonedx-npm --output-format json --output-file .genticode/raw/sbom-node.json || true"
```

---

## 9. Error Recovery Playbooks
- **Tool missing:** attempt install via brew/pipx, retry once; else record and stop.
- **ImportError:** recreate venv; reinstall; retry once.
- **Syntax error:** run `python -m pyflakes` or eslint to pinpoint; fix or revert last patch.
- **Stuck process:** kill group; mark TIMEOUT; retry once with 2× cap.
- **Corrupt venv:** remove `.venv`, recreate, reinstall.
- **Git conflict:** stash, merge `origin/main`, re-apply patch; if still broken, emit remediation.
- **Network fail:** backoff 5s, 15s; then stop.
- **Disk full:** clean `.genticode/cache/*` and `node_modules/.cache`.

---

## 10. Action Triggers
- “generate/scaffold” → create plan, dry-run diffs, write candidate bundle.
- “test/failing” → run pytest JSON, extract signatures.
- “scan/security” → semgrep + normalize.
- “sbom/license” → generate SBOMs, import vulnerabilities, evaluate policy.
- “report” → build HTML/SARIF from `report.json`.
- “compare/regression” → baseline vs current, enforce exit code.
- “timeout” → wrap with run-cap wrapper.
- “mac path” → probe Homebrew coreutils path.

---

## 11. Acceptance Evidence Bundle
- `.genticode/reports/AC_<sprint-id>.md` with AC checklist, timings, coverage, env, links to artifacts.
- Commit hash and tag changes if milestone closes.

---

## 12. Stop Conditions
- ACs met and gates pass → stop and push branch.
- ACs unmet or gates fail → follow Review Workflow; consider rollback to `pre-<sprint-id>` and retry with updated lessons.
