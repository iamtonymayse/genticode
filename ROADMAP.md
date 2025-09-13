# ROADMAP.md — Genticode v0.9

Milestones group cohesive features. Each has a codename: [sea-animal adjective] + [funny adverb] + [land animal], alliterative.

---

## 0.1 — Slippery swiftly Stoat
**Theme:** Core CLI, config, and artifact model.  
**Features:**
- CLI scaffold: init, check, report --html, baseline capture|clear.
- `.genticode/` layout, `policy.yaml`, `PRIORITY.yaml` stubs.
- Single normalized `report.json` with empty pack support.
**Acceptance criteria:**
- Commands function as specified and generate expected files.
- HTML and SARIF transforms from an empty report succeed.
- Runs on macOS and Linux; container build produced.
**Known limitations:** No packs enabled by default; no gating.

---

## 0.2 — Salty sneakily Serval
**Theme:** Prompt Hygiene pack MVP.  
**Features:**
- Prompt-like string detector for Python and TS/JS.
- `prompts.manifest.json` with IDs, hashes, roles, versions.
- Hygiene lints: missing IDs, version stamps, secret placeholders, giant URL trimming.
- Auto-fix for constant extraction and redaction.
**Acceptance criteria:**
- Detector recalls ≥90% on seeded corpus and FP rate ≤10%.
- Manifest generated during `check` and referenced in report.
- Auto-fix produces syntactically valid patches in both languages.
**Known limitations:** No SSOT mapping yet; heuristics first pass.

---

## 0.3 — Silvery suavely Skunk
**Theme:** Static pack with Semgrep.  
**Features:**
- Curated Semgrep rulesets for Python and TS/JS.
- Secrets and unsafe config checks.
- Normalization into unified report.
**Acceptance criteria:**
- Semgrep runs for both languages with ≤5% wrapper overhead.
- Findings show file, span, rule, severity, remediation.
- Parallel workers configurable; default based on CPU.
**Known limitations:** Quality and Supply packs not yet present.

---

## 0.4 — Spiny spryly Springbok
**Theme:** Baselines and CI gates.  
**Features:**
- Baseline capture and regression-vs-baseline gating.
- Budgets per pack and severity; `--strict` mode.
- CI examples for GitHub Actions and generic containers.
**Acceptance criteria:**
- New high-severity findings above budgets fail merges.
- Baseline removals pass and are recorded.
- CI artifacts include HTML and SARIF.
**Known limitations:** License policy not enforced yet.

---

## 0.5 — Sleek slyly Squirrel
**Theme:** Supply pack.  
**Features:**
- CycloneDX SBOM for Python and Node.
- Vulnerability import from pip-audit and npm audit.
- License allow/deny policy.
**Acceptance criteria:**
- SBOMs emitted reliably for common managers.
- Vulnerabilities normalized with fix suggestions.
- License policy enforced via budgets.
**Known limitations:** IAST still disabled.

---

## 0.6 — Spiffy spryly Stoat
**Theme:** Quality pack and reports.  
**Features:**
- Ruff/flake8 and ESLint integration mapped to severities.
- Prompt Hygiene included as Quality subgroup.
- Report HTML improvements and SARIF parity.
**Acceptance criteria:**
- Style/smell rules measured and budgeted.
- HTML report shows pack tabs and deltas since baseline.
**Known limitations:** Traceability partial.

---

## 0.7 — Stormy suavely Springhare
**Theme:** Traceability pack and docs resolver.  
**Features:**
- AC↔tests linkage via `PRIORITY.yaml` IDs and test markers.
- Docs resolver to attach AC text and coverage to report.
**Acceptance criteria:**
- Coverage by AC rendered in HTML and included in SARIF properties.
- Diffs since baseline shown per AC.
**Known limitations:** IDE surfacing minimal.

---

## 0.8 — Spunky sneakily Serval
**Theme:** IDE surfacing, perf, and security logging.  
**Features:**
- VS Code tasks or minimal extension reading `report.json` spans.
- Parallelism defaults, global time caps, safe logging and redaction.
**Acceptance criteria:**
- Editor shows locations for at least two pack types.
- CI time caps enforce hard stop and emit partial results gracefully.
**Known limitations:** IAST plugin interface only skeleton.

---

## 0.9 — Saline slyly Stoat
**Theme:** Parity, packaging, and IAST interface skeleton.  
**Features:**
- Python/TS parity audit and fixes across packs.
- Container image and pipx/npm install paths finalized.
- IAST null provider wired with stable CLI contract.
**Acceptance criteria:**
- Parity checklist passes for Static, Supply, Quality, Traceability, Prompt Hygiene.
- Install methods validated in clean environments.
- IAST interface callable with no-op provider and time caps.
**Known limitations:** No default runtime gates; IAST providers external.

---

## Notes on sequencing
- Prompt handling lands early (0.2) and is exercised on Genticode itself from 0.2 onward.
- Each milestone updates budgets and baselines to avoid friction.
