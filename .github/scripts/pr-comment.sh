#!/usr/bin/env bash
# pr-comment.sh — upsert one pull-request comment, keyed by a hidden marker.
#
#   pr-comment.sh <pr-number> <body-file> <marker>
#
# `gh pr comment --edit-last` edits whichever comment the token posted last,
# which is not necessarily ours: the build job and the device job each post a
# comment, and they silently overwrote one another. This edits the comment whose
# body starts with <marker>, and creates it only when no such comment exists.
set -euo pipefail

PR="${1:?usage: pr-comment.sh <pr> <body-file> <marker>}"
FILE="${2:?body file}"
MARKER="${3:?marker, e.g. <!-- runtime-probe -->}"
REPO="${GITHUB_REPOSITORY:?GITHUB_REPOSITORY is not set}"

[ -f "$FILE" ] || { echo "pr-comment: no such file: $FILE" >&2; exit 1; }

# Make sure the marker is the very first line, so the next run finds it.
if ! head -1 "$FILE" | grep -qF -- "$MARKER"; then
  { printf '%s\n' "$MARKER"; cat "$FILE"; } > "$FILE.tmp"
  mv "$FILE.tmp" "$FILE"
fi

id=$(gh api "repos/$REPO/issues/$PR/comments" --paginate \
       --jq ".[] | select(.body | startswith(\"$MARKER\")) | .id" 2>/dev/null | head -1 || true)

if [ -n "${id:-}" ]; then
  gh api -X PATCH "repos/$REPO/issues/comments/$id" -F body=@"$FILE" >/dev/null
  echo "pr-comment: updated #$id ($MARKER)"
else
  gh api -X POST "repos/$REPO/issues/$PR/comments" -F body=@"$FILE" >/dev/null
  echo "pr-comment: created ($MARKER)"
fi
