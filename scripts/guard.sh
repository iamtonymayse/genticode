#!/usr/bin/env bash
set -euo pipefail

ROOT="$(git rev-parse --show-toplevel 2>/dev/null || pwd)"
cd "$ROOT"

echo "Running guard checks..."

# 1) Obvious secret patterns
PATTERNS=(
  "AKIA[0-9A-Z]{16}"
  "ASIA[0-9A-Z]{16}"
  "aws_secret_access_key"
  "-----BEGIN (EC|RSA|OPENSSH) PRIVATE KEY-----"
  "password\s*="
  "x-api-key"
  "secret\s*="
  "token\s*="
)
RC=0
for p in "${PATTERNS[@]}"; do
  if rg -nEI "$p" --hidden --glob "!/.git/*" --glob "!/.genticode/cache/*" . | tee .genticode/logs/guard-secrets.txt; then
    echo "Guard: potential secret pattern detected: $p" >&2
    RC=2
  fi
done

# 2) Block large files (>5MB) outside caches
if command -v gfind >/dev/null 2>&1; then FIND=gfind; else FIND=find; fi
LARGE=$($FIND . -type f -size +5M \
  -not -path "./.git/*" \
  -not -path "./.genticode/cache/*" \
  -not -path "./node_modules/*" || true)
if [ -n "$LARGE" ]; then
  echo "Guard: large files detected outside cache:" >&2
  echo "$LARGE" | tee .genticode/logs/guard-largefiles.txt >&2
  RC=3
fi

# 3) Block common junk files
JUNK=$(rg -nI "\.env$|id_rsa|\.pem$" --hidden --glob "!/.git/*" --glob "!/.genticode/cache/*" . || true)
if [ -n "$JUNK" ]; then
  echo "Guard: junk or sensitive files detected:" >&2
  echo "$JUNK" | tee .genticode/logs/guard-junk.txt >&2
  RC=4
fi

if [ "$RC" -ne 0 ]; then
  echo "Guard checks failed (RC=$RC). Fix findings before pushing." >&2
  exit "$RC"
fi

echo "Guard checks passed."
