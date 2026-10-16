#!/usr/bin/env bash
set -euo pipefail

# git diff omits untracked replacement pages when a generated route changes.
# Porcelain includes those pages, deletions, staged changes and working-tree edits.
changes=$(git status --porcelain=v1 --untracked-files=all -- src/content/docs)
if [[ -n "$changes" ]]; then
  git diff -- src/content/docs
  git diff --cached -- src/content/docs
  printf '%s\n' "$changes"
  printf '%s\n' \
    'DRIFT: the committed site does not match its pinned generation inputs.' \
    'Commit regenerated content together with the input pin changes.'
  exit 1
fi
printf '%s\n' 'content: committed tree matches the pinned inputs (regeneration is a no-op).'
