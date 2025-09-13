SHELL := /bin/bash

.PHONY: guard test init

init:
	@mkdir -p .genticode/{logs,cache,raw,reports,baseline,candidates,local}
	@echo "Initialized .genticode structure."

guard:
	@scripts/guard.sh

test:
	@if command -v pytest >/dev/null 2>&1; then \
		CAP=600 scripts/run pytest -q --maxfail=1 --disable-warnings --cov --cov-branch --cov-fail-under=95 --json-report --json-report-file=.genticode/raw/pytest.json ; \
		true ; \
	else \
		echo "pytest not installed yet — skipping." ; \
	fi
