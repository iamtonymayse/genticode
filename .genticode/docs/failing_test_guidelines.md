# Failing Test Guidelines (Water Spider)

This project uses a multi‑pass attempts loop to diagnose and fix failures quickly without masking issues.

- Never edit or delete tests without an approved waiver in `.genticode/local/waivers/*.yaml` (approved: true, scope listed, evidence linked).
- Run attempts with time caps and full coverage:
  - `CAP=1200 ./run "pytest -q --maxfail=0 --disable-warnings --timeout=30 --cov --cov-branch --cov-fail-under=95 --json-report --json-report-file=.genticode/raw/pytest.json"`
  - `python scripts/attempt.py` to record the attempt.
- After each attempt, use `python scripts/lessons_decide.py --prev ... --curr ...` to decide `RETRY` vs `SPLIT`.
- Write lessons in `.genticode/local/LESSONS.md`, merge into `LESSONS_CURRENT.md` during review, and keep `LESSONS_ACCEPTED.md` append‑only.
- Determinism: keep seeds & versions pinned (see `tools/versions.lock`); re‑runs must be byte‑identical when inputs don't change.
