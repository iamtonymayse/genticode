Genticode 🧬

Policy‑driven guardrails for AI‑assisted coding: one run, one report, one gate.

Genticode reduces risk and noise when coding with AI. It is IDE‑neutral, CLI‑first, and local‑first. It targets Python and TypeScript/JavaScript parity and produces a single normalized report you can gate on in CI.

⸻

What Genticode Does
	•	Static, Supply, Quality, and Traceability packs run under one policy.
	•	Single artifact model: .genticode/report.json → transforms to sarif.json and report.html.
	•	Baselines and budgets: evaluate deltas by default so existing debt does not block you.
	•	Prompt hygiene: detect prompt‑like strings, enforce IDs/versions, and safe redaction.

Design sources: see ADDH_v0_9.md, PRD.md, ROADMAP.md, and SPRINT_PLAN.md.

⸻

The Lessons Loop ♻️ (central to Genticode)

Genticode bakes in a lightweight, local lessons learned loop that turns failed attempts into better future runs without nerfing tests or deleting guardrails.

Files (git‑ignored):

.genticode/local/LESSONS.md           # raw entries per Review sprint
.genticode/local/LESSONS_CURRENT.md   # merged active set (supersedes older)
.genticode/local/LESSONS_ACCEPTED.md  # audit trail of applied lessons
.genticode/local/LESSONS_GUIDE.md     # template and root‑cause method

How it works each sprint:
	1.	Start by reading LESSONS_CURRENT.md and apply its improved instructions and preventive controls.
	2.	After the Feature sprint, run the Review sprint: re‑run tests and gates.
	3.	If anything fails, record a concise 5‑Whys root cause, improved instructions, and preventive controls in LESSONS.md, then merge into LESSONS_CURRENT.md (superseding older guidance).
	4.	If the sprint was accepted and lessons were applied, copy those entries to LESSONS_ACCEPTED.md under the sprint ID.
	5.	If ACs were not met, reset to the pre-<sprint> tag and retry using the updated lessons.

Test‑nerfing safeguards:
	•	Traceability gates: AC IDs in PRIORITY.yaml must be covered by tests; missing coverage can fail the gate.
	•	Delta awareness: gates can alert on test deletions or coverage drops for READY ACs.
	•	Optionally add mutation testing later; never change tests just to go green—improve code or add better tests.

⸻

Quick Start

# Dev install (local repo)
python -m venv .venv && source .venv/bin/activate
pip install -r requirements-dev.txt  # test tooling
# Initialize Genticode in a project
make init
genticode init
genticode check
genticode baseline capture
genticode report --html
open .genticode/report.html  # macOS

Minimal policy to start (.genticode/policy.yaml):

version: 1
packs:
  static: {enabled: true, timeout_s: 600}
  supply: {enabled: true, timeout_s: 600}
  quality: {enabled: true, timeout_s: 1800}
  traceability: {enabled: true, timeout_s: 120}
severity_map: {info: 0, low: 20, medium: 50, high: 80, critical: 95}
budgets:
  secrets: {max_total: 0}
  licenses: {deny: [AGPL-3.0], fail_on_unknown: true}
progressive_enforcement: {phase: new_code_only}


⸻

Features at a Glance

Pack	What it does	Outputs
Static	Semgrep SAST, secrets/PII, API‑misuse curation	findings → report.json, SARIF rules
Supply	CycloneDX SBOM, license policy, vuln import (pip/npm/OSV)	SBOMs, normalized findings
Quality	Linters mapped to severities; flake rate tracking	metrics + findings
Traceability	AC↔tests links from PRIORITY.yaml, coverage and diffs	coverage matrix

Prompt hygiene is part of Static/Quality by default: detect prompt‑like strings, maintain a manifest, and enforce IDs/versions/redaction.

⸻

What you’ll see on first run
	•	.genticode/report.json with per‑pack sections and normalized findings.
	•	.genticode/sarif.json for PR annotations.
	•	.genticode/report.html static dashboard for local review.
	•	On first green run, capture a baseline; subsequent runs evaluate delta only.

⸻

Why this is different
	•	Policy‑driven, not model‑driven. Works with or without a specific AI model.
	•	Lessons, not lore. The lessons loop makes context cumulative and auditable.
	•	Gates you can live with. Start in warn, enforce on new code, then hard‑fail when you’re ready.

⸻

Limitations (v0.9)
	•	IAST is pluggable but off by default.
	•	Windows support is deferred in 0.x.
	•	Some advanced checks (e.g., mutation testing) are optional or planned.

⸻

Contributing
	•	Read the specs and plan: ADDH_v0_9.md, PRD.md, ROADMAP.md, SPRINT_PLAN.md, AGENTS.md.
	•	Write tests first; keep coverage ≥95% for changed code.
	•	Run scripts/guard.sh before pushing; never commit secrets.
	•	Open a PR with a concise AC checklist and a link to .genticode/report.html if relevant.

⸻

FAQ

Is this tied to any IDE or model?
No. CLI‑first; IDE extension is optional. Model‑agnostic.

Will this stop hallucinations?
It reduces impact via tests, prompts hygiene, and gates. It does not change model internals.

Can it block bad changes?
Yes. Secrets and license violations are hard gates by default; others can be budgeted and phased.

⸻

License

MIT — see LICENSE.
# Genticode — v0.9.x (Alpha)

Genticode is a lightweight, policy-driven CLI that orchestrates multiple packs (Prompt, Static, Supply, Quality, Traceability) and produces a unified report (`.genticode/report.json`) with HTML and SARIF transforms. It runs locally and in CI, applies progressive gates with baselines, and emphasizes safe, deterministic behavior.

## Quickstart

```
python -m genticode init
python -m genticode check
python -m genticode report --html --sarif
```

Artifacts are written under `.genticode/`. Baselines:

```
python -m genticode baseline capture
```

## Policy Example (`.genticode/policy.yaml`)

```
version: 1
progressive_enforcement: { phase: new_code_only }
packs:
  static: { enabled: true, timeout_s: 300, ruleset: ["p/python", "p/typescript"] }
  supply: { enabled: true, timeout_s: 300 }
  quality:{ enabled: true, timeout_s: 120 }
  prompt: { enabled: true, timeout_s: 120 }
  traceability: { enabled: true, timeout_s: 60 }
budgets:
  static: { high: 0 }
  prompt: { count: 100 }          # max prompts allowed (delta rules apply by phase)
  quality: { count: 500 }
  supply: { count: 0 }            # license violations by count
  traceability: { uncovered_delta_max: 0 }
```

## Hardening and Limits

- Per-pack timeouts enforced by the orchestrator; packs run in parallel.
- Large files are skipped by scanners (`GENTICODE_MAX_FILE_BYTES`, default 1 MiB).
- Logging redacts token-like strings by default.

## CI Tips

- Install tools as needed (ruff, eslint, semgrep, pip-audit, npm) for richer results.
- Always run `scripts/guard.sh` before pushing.
