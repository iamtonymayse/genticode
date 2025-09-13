# Genticode PRD v0.9

**Status:** Draft for greenfield implementation  
**Source of truth:** ADDH v0.9. This PRD traces every requirement to an ADDH aspect.

---

## 1. Scope and objectives

Genticode is a lightweight, policy-driven CLI that reduces AI-assisted coding failures without IDE lock-in and targets Python and TypeScript/JavaScript with parity. It runs locally and in CI, produces a single normalized report, and enforces progressive gates with baselines.

### In-scope
- Single CLI control plane and config.
- Four composable packs sharing one artifact model: Static, Supply, Quality, Traceability.
- Prompt-like string handling and hygiene as a first-class concern.
- Python and TS/JS parity across scanning, policies, and reporting.
- HTML and SARIF report transforms.
- CI gates with regression-vs-baseline semantics.

### Out of scope
- SaaS backend or persistent server.
- Mandatory IDE extension.
- Default IAST runtime gating (IAST is pluggable and off by default).

---

## 2. Actors and environments

- **SWE:** runs `genticode` locally and in pre-commit, fixes findings.
- **EM/Tech Lead:** owns policy budgets, baselines, and merge gates.
- **PM/QA:** reads report, checks AC ↔ tests status in Traceability pack.
- **CI:** executes `genticode check` and enforces budgets.

Environments: macOS and Linux dev hosts, Linux CI runners. Python 3.10+ and Node 18+ toolchains present when applicable.

---

## 3. Glossary

- **Pack:** A logical module that produces findings sharing the normalized artifact model. Packs: Static, Supply, Quality, Traceability, Prompt (hygiene) [Prompt is part of Quality but called out explicitly].
- **Baseline:** Accepted prior state used to compute deltas and enforce progressive budgets.
- **Budget:** Policy thresholds per severity or rule group.
- **Prompt-like string:** Any string literal intended for use by an LLM or agent, including embedded instructions or DSLs.

---

## 4. Functional requirements (FR) with acceptance criteria (AC) and ADDH traceability

### 4.1 Control plane and configuration
**FR-CLI-001** CLI commands exist: `init`, `check`, `report --html`, `baseline capture|clear`.  
AC: 
- Running `genticode init` creates `.genticode/` with `policy.yaml` and `PRIORITY.yaml` stubs.  
- `genticode check` produces `.genticode/report.json` with at least one pack’s results.  
- `genticode report --html` produces `.genticode/report.html`.  
- `genticode baseline capture` creates `.genticode/baseline/*` and subsequent `check` marks unchanged findings as baseline.  
Trace: cli.surface, ci.gates, report.formats, workspace.paths.

**FR-CONF-002** Central policy and priorities.  
AC:
- `.genticode/policy.yaml` defines budgets, pack toggles, and severity mappings.  
- `PRIORITY.yaml` hosts stable IDs for ACs and scope tags.  
Trace: governance.versioning, ci.gates.

**FR-ART-003** Single normalized report.  
AC:
- `.genticode/report.json` is the single source of results for all packs.  
- Converter produces `.genticode/sarif.json`.  
Trace: report.formats, normalization.schema.

### 4.2 Packs and findings

#### 4.2.1 Prompt Hygiene pack
**FR-PROMPT-010** Detect prompt-like strings in Python and TS/JS sources.  
AC:
- Detector finds string literals matching heuristics: long multi-line strings, role keywords, LLM markers, YAML/JSON fragments.  
- Produces findings with file, span, rule, and normalized evidence.  
Trace: generator.loop, quality, normalization.schema.

**FR-PROMPT-011** Prompt manifest.  
AC:
- `genticode check` emits `.genticode/prompts.manifest.json` referencing every detected prompt-like string with ID, source hash, inferred role, and version.  
Trace: generator.loop, governance.versioning.

**FR-PROMPT-012** Hygiene rules.  
AC:
- Lints cover injection risks, missing IDs, missing version stamps, long opaque URLs, secret placeholders, and model-leaking parameters.  
- Auto-fix offers safe redaction or constant extraction for Python and TS/JS.  
Trace: security.logging, scanners.semgrep, quality.

**FR-PROMPT-013** SSOT alignment hooks.  
AC:
- Optional mapping file allows associating prompt IDs to SSOT entries; discrepancies become findings.  
Trace: docs.resolver, generator.loop.

#### 4.2.2 Static pack
**FR-STAT-020** SAST integration.  
AC:
- Semgrep runs for Python and TS/JS with curated rule sets.  
- Findings are normalized and deduplicated across languages.  
Trace: scanners.semgrep, normalization.schema, perf.parallelism.

**FR-STAT-021** Secrets and config checks.  
AC:
- Secret checks and unsafe config patterns yield findings with remediation.  
Trace: security.logging, scanners.semgrep.

#### 4.2.3 Supply pack
**FR-SUP-030** SBOM generation and policy.  
AC:
- CycloneDX SBOM produced for Python (pip/poetry) and Node (npm/yarn).  
- License allow/deny policy enforced.  
Trace: sbom.cyclonedx, ci.gates.

**FR-SUP-031** Vulnerability lookup.  
AC:
- pip-audit and npm audit (or OSS index) findings normalized into the report with severity mapping and fix suggestions.  
Trace: sbom.cyclonedx, normalization.schema.

#### 4.2.4 Quality pack
**FR-QUAL-040** Style and smell gates.  
AC:
- Python: ruff or flake8 rules; Node: eslint rules; select rules mapped to severity budgets.  
- Prompt Hygiene pack integrates as a subgroup under Quality by default.  
Trace: report.formats, ci.gates.

#### 4.2.5 Traceability pack
**FR-TRACE-050** AC↔tests linkage.  
AC:
- Parser reads `PRIORITY.yaml` AC IDs and matches to tests via markers or filenames.  
- Report shows coverage by AC and diffs since last baseline.  
Trace: tests.runner, docs.resolver, normalization.schema.

### 4.3 CI gates and progressive enforcement
**FR-CI-060** Regression vs baseline.  
AC:
- New high-severity findings above budgets fail with non-zero exit.  
- Removals of baseline findings pass.  
Trace: ci.gates.

**FR-CI-061** Budgets per pack and severity.  
AC:
- Per-pack budgets defined; `--strict` flag enforces all proposed budgets.  
Trace: ci.gates.

**FR-CI-062** HTML and SARIF outputs in CI artifacts.  
AC:
- CI run emits `report.html` and `sarif.json` on success or failure.  
Trace: report.formats.

### 4.4 IDE and UX
**FR-IDE-070** Thin editor surfacing.  
AC:
- VS Code tasks or minimal extension shows file-spans from `report.json`.  
- No background daemon required.  
Trace: ide.integration.

### 4.5 IAST interface
**FR-IAST-080** Pluggable interface with null provider.  
AC:
- Stable CLI contract for running dynamic checks with time cap.  
- Null provider ships by default; runtime gating disabled unless configured.  
Trace: iast.interface, perf.parallelism.

### 4.6 Performance and safety
**FR-PERF-090** Parallelism and time caps.  
AC:
- Configurable worker count with default based on CPU.  
- Hard cap for total run time in CI.  
Trace: perf.parallelism.

**FR-SEC-091** Security logging and PII hygiene.  
AC:
- Logs redact secrets and limit payload sizes.  
- Debug logs gated by env var; default level is info.  
Trace: security.logging.

### 4.7 Packaging and workspace
**FR-PKG-100** Install and run anywhere.  
AC:
- `pipx` and `npm` install options or a single container image.  
- Works from repo root with standard workspace paths.  
Trace: workspace.paths, cli.surface.

---

## 5. Non-functional requirements

- Deterministic outputs for the same inputs and policy.  
- Local-first, no network required except to fetch rulepacks or advisories when enabled.  
- Extensible rulepacks and adapters via config.  
- Privacy: no telemetry by default; opt-in only.

---

## 6. Design constraints (non-criteria)

- No IDE lock-in or Cursor-only behaviors.  
- No SaaS control plane. Artifacts are local or CI artifacts.  
- IAST off by default.  
- Keep SSOT light: only `PRIORITY.yaml` and `policy.yaml` are mandatory.  
- Python 3.10+ and Node 18+ only.  
- macOS and Linux supported; Windows not required in 0.x.

---

## 7. Traceability matrix (ADDH aspect → PRD requirements)

- ci.gates → FR-CI-060, FR-CI-061, FR-CI-062  
- cli.surface → FR-CLI-001, FR-PKG-100  
- docs.resolver → FR-PROMPT-013, FR-TRACE-050  
- generator.loop → FR-PROMPT-010..013  
- governance.versioning → FR-CONF-002, FR-PROMPT-011  
- iast.interface → FR-IAST-080  
- ide.integration → FR-IDE-070  
- lessons.mcp → reserved for 0.9.x; not required in 0.9 baseline  
- normalization.schema → FR-ART-003, FR-STAT-020, FR-SUP-031, FR-TRACE-050  
- perf.parallelism → FR-PERF-090, FR-IAST-080  
- report.formats → FR-ART-003, FR-CI-062, FR-QUAL-040  
- sbom.cyclonedx → FR-SUP-030  
- scanners.semgrep → FR-STAT-020, FR-STAT-021  
- security.logging → FR-SEC-091, FR-PROMPT-012  
- tests.runner → FR-TRACE-050  
- workspace.paths → FR-PKG-100, FR-CLI-001

---

## 8. Acceptance test suite outline

- CLI smoke tests for each subcommand.  
- Pack-specific golden tests with normalized report fixtures.  
- Prompt detector unit tests with positive/negative corpora.  
- Baseline regression tests with controlled delta scenarios.  
- Performance tests for time caps and worker scaling.  
- SARIF and HTML snapshot tests.

---

## 9. Risks and mitigations

- False positives in prompt detection → curated heuristics, opt-out annotations.  
- Rulepack drift → lockfile and version pins.  
- Language parity gaps → milestone-driven parity checks in CI.  
- Developer friction → baseline-first approach and budgets by severity.
