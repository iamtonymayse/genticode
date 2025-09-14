% Failing Test Adjudication Guidelines (Concise)

- Classify: Requirements, Design, Code, Test, Tooling, Environment, Process.
- Collect all failures in a single run; do not stop at first red.
- Attach failing test names and logs; do not edit or delete tests without waiver and evidence.
- Perform 5 Whys (3–5 lines) and capture root cause.
- Write lessons in `.genticode/local/LESSONS.md` and merge to `LESSONS_CURRENT.md`.
- If any failures: tag pre-sprint, reset to tag, regenerate product code guided by lessons. No manual patches to product code to “make tests pass”.
- Coverage must stay ≥95% for sprint-owned code; prefer small, composable functions.
