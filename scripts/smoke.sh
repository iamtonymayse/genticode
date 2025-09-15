#!/usr/bin/env bash
set -euo pipefail

# Minimal local smoke: run CLI on a temp repo directory
TMP=$(mktemp -d)
trap 'rm -rf "$TMP"' EXIT

pushd "$TMP" >/dev/null
  echo "# stub" > PRIORITY.yaml
  python3 -m genticode init
  python3 -m genticode check || true
  python3 -m genticode report
  echo "Smoke OK: $(ls -1 .genticode | wc -l) artifacts"
popd >/dev/null

