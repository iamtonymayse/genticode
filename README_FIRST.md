# Genticode v0.9 — Starter Repo

This archive contains the minimal files to kick off development with the sprint plan, lessons workflow, and guard rails.

Quick start
1) Create a git repo, commit this tree, and add a remote.
2) Ensure macOS with Homebrew and coreutils installed (see AGENTS.md §2).
3) Create a venv: `python3 -m venv .venv && source .venv/bin/activate`.
4) Optional: `pip install -r requirements-dev.txt` to run tests when they appear.
5) Read `SPRINT_PLAN.md` and start at Sprint 0.1a. Read `.genticode/local/LESSONS_CURRENT.md` if it exists.
6) Before pushing, run: `make guard`.

Files of interest
- ADDH_v0_9.md, PRD.md, ROADMAP.md, SPRINT_PLAN.md, AGENTS.md
- .genticode/* folders and lessons scaffold
- scripts/guard.sh and scripts/run
- .gitignore
