# Genticode — Architecture, Design, and Decision History (ADDH)

**Version:** 0.9  
**Date:** 2025-09-13  
**Status:** Baseline approved for greenfield implementation  
**Source of Truth:** This ADDH is authoritative for Genticode design decisions. The PRD is informative.

---

## 1. Executive summary
Genticode is a lightweight, policy-driven system that defends software teams from common AI-assisted coding failures. It reduces security risk, drift, style smell, and prompt misuse without locking into a specific IDE. It targets Python and TypeScript/JavaScript with parity. Genticode runs as a standalone CLI and can also operate as a **pack** within Genticore. A thin editor extension surfaces results but the CLI is the control plane.

**Design thesis**
- One run, one report, one gate.  
- Progressive enforcement with baselines to avoid friction.  
- Four composable **packs** share one artifact model: **Static, Supply, Quality, Traceability**.  
- Prompt handling is first-class.  

---

## 2. Goals and non-goals
### 2.1 Goals
- Reduce high-severity defects introduced during AI-assisted development.  
- Prevent architectural and requirement drift.  
- Enforce prompt hygiene for code that includes prompt-like strings.  
- Maintain Python and TS/JS parity across scanners, gates, and reports.  
- Keep teams fast by minimizing local friction and by default evaluating **delta** vs **baseline**.  

### 2.2 Non-goals
- Heavy SSOT beyond `PRIORITY.yaml` and a single `policy.yaml`.  
- IDE lock-in or Cursor-only behavior.  
- Default IAST runtime gating. IAST remains pluggable and off by default.  
- SaaS backend. Artifacts are local or CI-only, with optional publishing as static files.

---

## 3. Users and value
- **Software Engineers (SWE):** Fast feedback, precise remediation, low-noise gates, prompt linting.  
- **Engineering Managers (EM):** Policy-as-code, risk bands, trend KPIs, license and secret compliance.  
- **Product Managers (PM):** Acceptance criteria ↔ test traceability, change diffs for releases.  

---

## 4. Operating model
### 4.1 Single CLI
```
# in repo root
$ genticode init                # create .genticode/ with policy starter
$ genticode check               # run all enabled packs, write report.json
$ genticode report --html       # transform report.json → report.html
$ genticode baseline capture    # snapshot current findings as baseline
$ genticode baseline clear      # remove baseline
```

### 4.2 Configuration
- `.genticode/policy.yaml` — central policy, budgets, mappings, pack toggles.  
- `PRIORITY.yaml` — scope, states, and acceptance criteria (AC) with stable IDs.  
- Optional `.genticode/overrides/*.yaml` for team or branch-specific deltas.  

### 4.3 Artifacts
- `.genticode/report.json` — **single source of results**.  
- `.genticode/sarif.json` — transform of report for code hosts.  
- `.genticode/report.html` — static, no-backend dashboard.  
- `.genticode/baseline/` — snapshot of prior accepted state.  
- `.genticode/cache/` — rulepacks, vuln DB slices, SBOMs.  

### 4.4 Gate engine
- Uniform **Budgets** per category (secrets, licenses, API misuse, vuln severity, flake rate, perf, size, AC coverage…).  
- **Baseline** vs **Delta** evaluation mode, defaulting to **Delta**.  
- **Progressive enforcement**: Week 1 warn → Week 2 new-code budgets → Week 3 hard gate.  
- **Timeouts and parallelism** per pack; graceful degradation to `warn_on_timeout: true`.  

---

## 5. Architecture
```
+--------------------+
|      CLI/Driver    |  genticode check | report | baseline
+---------+----------+
          | orchestrates
          v
+--------------------+       +-----------------+
|       Core         |<----->|   Policy (YAML) |
| - timeouts         |       | - budgets       |
| - concurrency      |       | - mappings      |
| - caching          |       | - pack toggles  |
+----+---+---+-------+       +---------+-------+
     |   |   |                         |
     v   v   v                         v
 [Static][Supply][Quality][Traceability pack modules]
     \   |   /                         |
      \  |  /                          |
        v v                            v
     Findings, Traces, Evidence  <---- Gate Engine
                |
                v
           ReportManager → report.json → {sarif.json, report.html}
```

### 5.1 Packs
**Static pack**  
- Secrets and PII scanning (multiple providers supported).  
- Semgrep SAST for Python and TS/JS with curated rules for API misuse, auth, crypto, file/OS, async, SSRF, XSS, command exec.  
- Prompt linting: registry enforcement, interpolation safety, size hints, secret redaction.  
- Style and smell lints normalized to unified severities.  

**Supply pack**  
- SBOM generation (CycloneDX).  
- Known-vulnerability mapping from SBOM.  
- License detection and **license policy gate** (deny list and unknown).  
- Optional provenance stamp in artifacts.  

**Quality pack**  
- Test runner integration (pytest; npm/yarn/pnpm test).  
- Flaky-test detection via automatic re-runs and flake rate tracking.  
- Optional hooks for mutation testing (off by default).  
- Performance and size **Budgets** for Py (pytest-benchmark) and JS (bundle budgets).  

**Traceability pack**  
- AC ↔ Test traceability using `PRIORITY.yaml` IDs and test markers.  
- Change-risk scoring from churn, diff size, fan-out, and complexity.  
- Release-notes diff computed from `PRIORITY.yaml` evolution.  

---

## 6. Policy model
### 6.1 Starter `policy.yaml`
```yaml
version: 1
packs:
  static: {enabled: true, timeout_s: 600}
  supply: {enabled: true, timeout_s: 600}
  quality: {enabled: true, timeout_s: 3600}
  traceability: {enabled: true, timeout_s: 120}
severity_map: {info: 0, low: 20, medium: 50, high: 80, critical: 95}
budgets:
  secrets: {max_total: 0}
  licenses: {deny: [AGPL-3.0], fail_on_unknown: true}
  api_misuse: {max_high_per_1k_loc: 0}
  vulns: {max_critical: 0, max_high: 0}
  flake_rate: {warn_gt: 0.02, fail_gt: 0.05, window: 50}
  perf_ms: {warn_gt: 110, fail_gt: 150}
  bundle_kb: {warn_gt: 250, fail_gt: 350}
  ac_coverage: {min_pct: 1.0}
progressive_enforcement:
  phase: new_code_only  # warn | new_code_only | hard
risk_bands: {info: "<20", warn: "20-49", high: "50-79", critical: ">=80"}
```

### 6.2 Normalization
All tool outputs are mapped to the unified severity scale and a 0–100 **risk score**. The Gate engine evaluates Budgets on both raw counts and risk-weighted totals.

---

## 7. Prompt registry and linting
- `prompts/` or `.genticode/prompts/` holds prompts as YAML or JSON with metadata: ID, purpose, variables, max_tokens guidance, safety notes.  
- Lints:  
  - variables must be explicitly declared and typed;  
  - interpolation must use safe helpers;  
  - secrets and PII are forbidden;  
  - context size estimates must be present;  
  - each prompt references relevant guideline docs for the resolver.  
- Findings integrate with Static pack severities and the single gate.  

---

## 8. Editor integration
- Thin VS Code/Cursor extension invokes the CLI, displays diagnostics, and opens `report.html`.  
- No extension-only features. All functions must be reproducible via CLI.  

---

## 9. CI integrations
- Reference jobs for GitHub Actions, GitLab CI, and Jenkins.  
- Defaults: cache reuse, per-pack concurrency, total time cap of 60 minutes, delta-mode enforcement.  
- Status checks driven by `sarif.json` and exit code from the Gate engine.  

---

## 10. Reporting
- **report.json** schema contains Findings, Budgets, Traces, Evidence, and computed Risk.  
- **sarif.json** transform supports inline PR annotations.  
- **report.html** is a static dashboard with:  
  - overview KPIs;  
  - trend spark lines;  
  - per-pack tabs;  
  - risk bands and suggested next actions;  
  - AC coverage matrix and release-notes diff.  

---

## 11. Baseline and delta
- First run captures a **baseline** snapshot.  
- The Gate evaluates **delta** by default to reduce noise and friction.  
- `--full` flag forces full-evaluation for periodic sweeps.  

---

## 12. Default enforcement
- **Week 1:** all budgets warn only.  
- **Week 2:** budgets apply to new and changed files; secrets and licenses are hard gates.  
- **Week 3:** hard gates for all budgets as configured.  

---

## 13. Roadmap and milestone alignment
### 13.1 v0.9 scope (ship together)
1) Secrets/PII scanning + CI gate  
2) License policy gate from SBOM  
3) API-misuse rules pack (Py/TS)  
4) Flaky-test detector integrated into test runner  
5) Change-risk scoring  
6) AC ↔ Test traceability from `PRIORITY.yaml`  
7) Release-notes diff from `PRIORITY.yaml`  

**Impact:** closes the highest-value risk at low cost; moves direct coverage to ~70–75% of common AI-coding complaints.

### 13.2 Post-0.9 candidates
- Performance and bundle-size budgets as first-class Budgets.  
- Static dashboard trends and cross-repo views.  
- Mutation testing hooks (mutmut, Stryker) as opt-in.  
- IAST providers behind feature flag with clear contract.  

---

## 14. Implementation notes
- Keep everything in `.genticode/` with deterministic, repo-relative paths.  
- Treat third-party tool versions as pinned in `policy.yaml` to ensure reproducibility.  
- Rulepack curation is part of the repo and versioned.  
- Do not write proprietary or sensitive content to console by default; prefer artifacts.  

---

## 15. Security and privacy
- Local-first processing.  
- Redact or hash any sensitive strings that must appear in evidence.  
- Explicit allowlists for domains and licenses.  
- No outbound network calls unless `--allow-net` is set in policy for specific providers.  

---

## 16. Open questions
- How strict should default API-misuse budgets be in early adoption for large monorepos?  
- Do we enforce test naming conventions for AC traceability across all frameworks or maintain adapters?  
- What is the minimal acceptable accuracy for change-risk scoring before gating on it?  

---

## 17. Decision log (abridged)
- **Unified pipeline:** Consolidated reporters and gates into one artifact model and one gate engine.  
- **Packs composition:** API-misuse merged into Static; flake detection composed into test runner; license gate composed into Supply; release-notes diff composed into Traceability.  
- **Progressive enforcement:** Three-phase rollout to minimize friction.  
- **Baseline-first:** Default delta evaluation to reduce noise.  
- **Thin editor:** Extension is a client of the CLI.  
- **IAST off by default:** Feature-flag only.  
- **Prompt-first:** Prompt registry and lints are mandatory when prompts exist.  

---

## 18. Changelog
- **0.9 (2025-09-13):** Unified policy-driven design; single CLI; single artifact model; single gate; four-pack architecture; prompt registry and lints; progressive enforcement; baseline/delta; ranked 0.9 scope.  
- **0.8:** Cursor-first MVP concepts and early pack separation; no unified gate; limited prompt handling.  

---

## 19. Glossary
- **Pack:** A module that produces Findings/Traces under a shared policy.  
- **Finding:** A normalized item with severity, location, and remediation.  
- **Trace:** A linkage across commits, ACs, and tests.  
- **Budget:** A numeric or boolean constraint evaluated by the gate engine.  
- **Baseline:** Accepted snapshot of findings used to compute deltas.  
- **AC:** Acceptance Criterion identified in `PRIORITY.yaml`.  

---

## 20. Acceptance criteria for v0.9
- Running `genticode check` on a Python or TS/JS repo produces a single `report.json` and exits with a gate status matching policy.  
- Secrets and license gates fail appropriately.  
- API-misuse rules annotate real violations in both languages with normalized severities.  
- Test runner integrates flake detection and emits quality findings.  
- `PRIORITY.yaml` IDs map to tests and render an AC coverage matrix.  
- `report.html` loads without backend and reflects the same data as `report.json`.  

---

## 21. Risks and mitigations
- **Rule noise:** Start in warn mode and ship baseline. Curate rulesets with suppression affordances.  
- **Tooling variance across OS/CI:** Pin versions and capture env details in Evidence.  
- **Adoption drag:** Provide one-command onboarding with sensible defaults and progressive enforcement.  

---

End of ADDH v0.9.
