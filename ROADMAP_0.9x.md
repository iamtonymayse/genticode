# ROADMAP — Genticode v0.9.x Stabilization

Purpose: deliver post‑v0.9 fixes in cohesive milestones with explicit review/reset steps after every feature sprint.

## Milestone 0.9.1 — Policy, Gates, Baselines, SARIF
- Policy engine with YAML loading + validation
- Progressive enforcement phases
- Baseline/delta across all packs
- Unified SARIF transform

## Milestone 0.9.2 — Orchestration and Static Completion
- Orchestrator + Pack interface
- Static pack completion: secrets/PII, normalization, configurable rulesets

## Milestone 0.9.3 — Supply, Quality
- Supply: vuln import (pip‑audit, npm/OSV), license budgets solid
- Quality: ruff/flake8, eslint, flaky‑test detector

## Milestone 0.9.4 — Traceability and Hardening
- Traceability AC↔tests coverage matrix + diffs
- Security hardening (subprocess, path/size limits), concurrency/time caps
- Integration tests, policy examples, better errors
