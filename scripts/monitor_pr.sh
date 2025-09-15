#!/usr/bin/env bash
set -euo pipefail

# Monitor a GitHub PR's checks and enforce hard gates via exit codes.
# Usage:
#   scripts/monitor_pr.sh owner/repo PR_NUMBER [--rerun-failures]
# Env:
#   GH_TOKEN (optional, recommended) to increase rate limits and enable reruns
#   GITHUB_API (optional) default https://api.github.com

REPO_SLUG=${1:-}
PR_NUM=${2:-}
RERUN=${3:-}

if [[ -z "${REPO_SLUG}" || -z "${PR_NUM}" ]]; then
  echo "Usage: $0 owner/repo PR_NUMBER [--rerun-failures]" >&2
  exit 64
fi

if ! command -v jq >/dev/null 2>&1; then
  echo "jq not found. Install jq first (brew install jq)." >&2
  exit 127
fi

API=${GITHUB_API:-"https://api.github.com"}
AUTH_HEADER=()
if [[ -n "${GH_TOKEN:-}" ]]; then
  AUTH_HEADER=( -H "Authorization: Bearer ${GH_TOKEN}" )
fi

owner=${REPO_SLUG%%/*}
repo=${REPO_SLUG##*/}

hdr=( -H "Accept: application/vnd.github+json" -H "X-GitHub-Api-Version: 2022-11-28" )

get_json() {
  local url=$1
  curl -fsSL "${API}${url}" "${hdr[@]}" ${AUTH_HEADER:+"${AUTH_HEADER[@]}"}
}

post_json() {
  local url=$1
  curl -fsSL -X POST "${API}${url}" "${hdr[@]}" ${AUTH_HEADER:+"${AUTH_HEADER[@]}"}
}

# 1) Fetch PR details
pr_json=$(get_json "/repos/${owner}/${repo}/pulls/${PR_NUM}")
head_sha=$(jq -r .head.sha <<<"$pr_json")
head_label=$(jq -r .head.label <<<"$pr_json")
pr_title=$(jq -r .title <<<"$pr_json")

if [[ -z "$head_sha" || "$head_sha" == "null" ]]; then
  echo "Failed to resolve head SHA for PR ${REPO_SLUG}#${PR_NUM}" >&2
  exit 70
fi

echo "PR: ${REPO_SLUG}#${PR_NUM} — ${pr_title}"
echo "Head: ${head_label} @ ${head_sha}"

# 2) Fetch check runs for the head SHA
checks_json=$(get_json "/repos/${owner}/${repo}/commits/${head_sha}/check-runs")

total=$(jq -r .total_count <<<"$checks_json")
names=$(jq -r '.check_runs[].name' <<<"$checks_json" | wc -l | tr -d ' ')

# Tally conclusions and statuses
success=$(jq -r '[.check_runs[] | select(.conclusion=="success")] | length' <<<"$checks_json")
failure=$(jq -r '[.check_runs[] | select(.conclusion=="failure")] | length' <<<"$checks_json")
cancelled=$(jq -r '[.check_runs[] | select(.conclusion=="cancelled")] | length' <<<"$checks_json")
timed_out=$(jq -r '[.check_runs[] | select(.conclusion=="timed_out")] | length' <<<"$checks_json")
action_required=$(jq -r '[.check_runs[] | select(.conclusion=="action_required")] | length' <<<"$checks_json")
neutral=$(jq -r '[.check_runs[] | select(.conclusion=="neutral")] | length' <<<"$checks_json")
skipped=$(jq -r '[.check_runs[] | select(.conclusion=="skipped")] | length' <<<"$checks_json")
queued=$(jq -r '[.check_runs[] | select(.status=="queued")] | length' <<<"$checks_json")
in_progress=$(jq -r '[.check_runs[] | select(.status=="in_progress")] | length' <<<"$checks_json")

echo "Checks: total=${total} (success=${success}, failed=${failure}, cancelled=${cancelled}, timed_out=${timed_out}, action_required=${action_required}, neutral=${neutral}, skipped=${skipped}, queued=${queued}, in_progress=${in_progress})"

# 3) Summarize failing checks
fail_list=$(jq -r '.check_runs[] | select((.conclusion=="failure") or (.conclusion=="timed_out") or (.conclusion=="cancelled") or (.conclusion=="action_required")) | "- " + .name + " — " + (.details_url // .html_url // "")' <<<"$checks_json")

if [[ -n "$fail_list" ]]; then
  echo "Failing checks:" && echo "$fail_list"
fi

# 4) Fetch workflow runs summary (GitHub Actions)
runs_json=$(get_json "/repos/${owner}/${repo}/actions/runs?head_sha=${head_sha}&per_page=100")
wr_total=$(jq -r '.total_count' <<<"$runs_json")
wr_success=$(jq -r '[.workflow_runs[] | select(.conclusion=="success")] | length' <<<"$runs_json")
wr_failed=$(jq -r '[.workflow_runs[] | select(.conclusion=="failure")] | length' <<<"$runs_json")
wr_cancelled=$(jq -r '[.workflow_runs[] | select(.conclusion=="cancelled")] | length' <<<"$runs_json")
wr_timed=$(jq -r '[.workflow_runs[] | select(.conclusion=="timed_out")] | length' <<<"$runs_json")
wr_inprog=$(jq -r '[.workflow_runs[] | select(.status=="in_progress" or .status=="queued")] | length' <<<"$runs_json")

echo "Workflows: total=${wr_total} (success=${wr_success}, failed=${wr_failed}, cancelled=${wr_cancelled}, timed_out=${wr_timed}, queued/in_progress=${wr_inprog})"

# 5) Optional: rerun failures if asked and token present
if [[ "${RERUN:-}" == "--rerun-failures" ]]; then
  if [[ -z "${GH_TOKEN:-}" ]]; then
    echo "--rerun-failures requested but GH_TOKEN is not set; skipping reruns." >&2
  else
    mapfile -t failed_ids < <(jq -r '.workflow_runs[] | select(.conclusion=="failure" or .conclusion=="timed_out" or .conclusion=="cancelled") | .id' <<<"$runs_json")
    if (( ${#failed_ids[@]} > 0 )); then
      echo "Rerunning ${#failed_ids[@]} failed workflow run(s)..."
      for id in "${failed_ids[@]}"; do
        post_json "/repos/${owner}/${repo}/actions/runs/${id}/rerun" >/dev/null || {
          echo "Failed to trigger rerun for run ${id}" >&2
        }
      done
    else
      echo "No failed runs to rerun."
    fi
  fi
fi

# 6) Exit codes for hard gates
# - 2: any failures (failure, cancelled, timed_out, action_required)
# - 1: no failures but queued/in_progress present
# - 0: all success or skipped/neutral only

hard_fail=$(( failure + cancelled + timed_out + action_required ))
if (( hard_fail > 0 )); then
  exit 2
fi

if (( queued + in_progress > 0 || wr_inprog > 0 )); then
  exit 1
fi

exit 0
