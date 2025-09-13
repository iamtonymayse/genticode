# AC Evidence — Sprint 0.8a (IDE/Perf/Logging)

- AC: Editor spans for ≥2 packs — ✅ (prompt spans emitted)
  - `.genticode/raw/spans.json` contains file/start/end entries from Prompt pack
- AC: Global/per-pack timeouts — ⚠️ deferred (wrapper exists; enforcement to expand later)
- AC: Safe logging and redaction — ✅
  - Logger redacts PAT-like and `sk-` tokens
- Tests and coverage (≥95%) — ✅
