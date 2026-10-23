#!/usr/bin/env bash
# probe-inputs.sh — resolve the probe options once, for both jobs.
#
#   probe-inputs.sh "<allow_no_bridge>" "<strict>" "<force_trial>" "<scenario>"
#
# Exports ALLOW_NO_BRIDGE / STRICT / FORCE_TRIAL / SCENARIO to $GITHUB_ENV.
#
# Why a file: `workflow_dispatch` is not always available. A GitHub App token
# can push to a branch but is refused by the dispatch API (403 "Resource not
# accessible by integration"), so a run has to be started by a push. In that
# case runtime-probe/probe-inputs.json acts as a one-shot override:
#
#   { "allow_no_bridge": true, "force_trial": true, "strict": false,
#     "scenario": "abi-smoke" }
#
# Delete it after the run — every push to the PR otherwise spends a trial
# session, and the trial allows one session per credential.
set -euo pipefail

allow="${1:-false}"; allow="${allow:-false}"
strict="${2:-true}"; strict="${strict:-true}"
force="${3:-false}"; force="${force:-false}"
scenario="${4:-}"

FILE="runtime-probe/probe-inputs.json"

if [ -f "$FILE" ]; then
  if ! jq -e . "$FILE" >/dev/null 2>&1; then
    echo "::error::$FILE is not valid JSON — refusing to guess probe options."
    exit 1
  fi
  echo "::warning::$FILE present — overriding the dispatch inputs for this run."
  jq -r 'to_entries[] | "  \(.key)=\(.value)"' "$FILE"

  v=$(jq -r 'if has("allow_no_bridge") then (.allow_no_bridge|tostring) else "" end' "$FILE")
  [ -n "$v" ] && allow="$v"
  v=$(jq -r 'if has("strict") then (.strict|tostring) else "" end' "$FILE")
  [ -n "$v" ] && strict="$v"
  v=$(jq -r 'if has("force_trial") then (.force_trial|tostring) else "" end' "$FILE")
  [ -n "$v" ] && force="$v"
  v=$(jq -r 'if has("scenario") then (.scenario|tostring) else "" end' "$FILE")
  [ -n "$v" ] && scenario="$v"
fi

{
  echo "ALLOW_NO_BRIDGE=$allow"
  echo "STRICT=$strict"
  echo "FORCE_TRIAL=$force"
  echo "SCENARIO=$scenario"
} >> "${GITHUB_ENV:?GITHUB_ENV is not set}"

echo "resolved: allow_no_bridge=$allow strict=$strict force_trial=$force scenario=${scenario:-<event name>}"
