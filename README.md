
# Genticode 🧬

> Policy‑driven guardrails for AI‑assisted coding: one run, one report, one gate.

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

Status: v0.97.0‑beta “Water Spider”

Genticode reduces risk and noise when coding with AI. It is IDE‑neutral, CLI‑first, and local‑first. It targets Python and TypeScript/JavaScript parity and produces a single normalized report you can gate on in CI.

---

## Visual Overview

### Team Genticode vs the Chaos Monster
![Team vs Monster](images/01_team_vs_monster.png)

### Pipeline: One run → One report → One gate
![Pipeline](images/02_pipeline.png)

### The Lessons Loop
![Lessons Loop](images/03_lessons_loop.png)

### Policy Phases
![Policy Phases](images/04_policy_phases.png)

### Packs → Outputs
![Pack Mapping](images/05_pack_mapping.png)

---

## What Genticode Does

- **Static, Supply, Quality, and Traceability packs** run under one policy.  
- **Single artifact model:** `.genticode/report.json` → transforms to `sarif.json` and `report.html`.  
- **Baselines and budgets:** evaluate deltas by default so existing debt does not block you.  
- **Prompt hygiene:** detect prompt‑like strings, enforce IDs/versions, and safe redaction.  

Design sources: [ADDH_v0_9.md](ADDH_v0_9.md), [PRD.md](PRD.md), [ROADMAP.md](ROADMAP.md), [SPRINT_PLAN.md](SPRINT_PLAN.md).

---

## The Lessons Loop (central)

Genticode encodes a multi‑pass, evidence‑driven loop to turn red test runs into better future runs **without** nerfing tests.

- Run the full suite once per attempt with timeouts.  
- Adjudicate failures (CODE_FIX, TEST_UPDATE with requirement proof, HARNESS_UPDATE, FLAKY, REQUIREMENT_GAP, KNOWN_FAIL).  
- Write 5‑Whys lessons and preventive controls; merge to `LESSONS_CURRENT.md`.  
- Reset to the pre‑sprint tag, rebuild with lessons, retry. Cap attempts; split if failures persist.  
- Test edits require a waiver with evidence; deletions are blocked.

---

## Quick Start

```bash
python -m venv .venv && source .venv/bin/activate
pip install -r requirements-dev.txt
make init
genticode init
genticode check
genticode baseline capture
genticode report --html
open .genticode/report.html
```

Minimal policy (`.genticode/policy.yaml`):
```yaml
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
```

---

## Contributing

- Keep coverage ≥95% for changed code.  
- Run `scripts/guard.sh` before pushing; never commit secrets.  
- Include an AC checklist in PRs and link to `.genticode/report.html` if relevant.

## License

MIT — see [LICENSE](LICENSE).
