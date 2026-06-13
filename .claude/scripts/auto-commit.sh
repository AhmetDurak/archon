#!/usr/bin/env bash
set -euo pipefail

REPO_ROOT="$(git -C "$(dirname "$0")" rev-parse --show-toplevel)"
MSG_FILE="$REPO_ROOT/.claude/pending_commit.txt"

[ -f "$MSG_FILE" ] || exit 0

COMMIT_MSG="$(cat "$MSG_FILE")"
[ -n "$COMMIT_MSG" ] || exit 0

cd "$REPO_ROOT"

if git diff --quiet && git diff --cached --quiet && [ -z "$(git ls-files --others --exclude-standard)" ]; then
    rm "$MSG_FILE"
    exit 0
fi

git add -A
git commit -m "$COMMIT_MSG"
rm "$MSG_FILE"
