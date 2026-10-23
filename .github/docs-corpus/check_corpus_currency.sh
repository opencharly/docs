#!/usr/bin/env bash
# check_corpus_currency.sh — REPORT the pinned corpus's currency. It never fails.
#
# The corpus pin is advanced by a MANUAL act after the corpus lands, so the site
# trails the corpus by however long nobody ran the regeneration — and the drift
# gate CANNOT see it: the PINNED corpus regenerates its own (old) pages
# perfectly, so a stale corpus is invisible to it. The drift gate answers "does
# the committed content match what the pinned inputs generate?" (yes, always);
# this answers the second question — "is the pinned corpus itself current?".
#
# The answer is REPORTED, never failed. A corpus that is behind is an advance
# available NOW — the same shape the pin contract calls `behind`: a reportable
# state, not a broken edge. A gate that FAILED on it would be red on every push
# until somebody ran the regeneration PR, and the remedy is that PR, not a gate.
#
# Usage: check_corpus_currency.sh <superproject-root> [<corpus-dir>]
# Prints exactly one line:
#   corpus pin: <pinned> is <state> (merged main: <tip>)
# Exit status is 0 in EVERY state, including a divergence and a missing corpus:
# a report that could fail the build would be a gate, and this is not one.
set -u

root=${1:-.}
corpus=${2:-marketplace}
dir="$root/$corpus"

report() {
  echo "corpus pin: $1 is $2 (merged main: $3)"
}

# The pin is the superproject's INDEX entry — the gitlink it records — not the
# checkout's HEAD. A checkout that is not at the pin is a different question
# (and the checkout audit asks it).
if ! pinned=$(git -C "$root" rev-parse --verify -q "HEAD:$corpus" 2>/dev/null); then
  report "(no pin)" "not pinned — the superproject records no gitlink for '$corpus'" "(unknown)"
  exit 0
fi

if ! git -C "$dir" rev-parse --verify -q HEAD >/dev/null 2>&1; then
  report "$pinned" "not materialized — the corpus has no checkout here" "(unknown)"
  exit 0
fi

# The corpus's merged main, as the remote sees it right now. The fetch brings
# the tip's objects in, so the ancestry test below is decidable rather than
# unanswerable.
if ! git -C "$dir" fetch --quiet origin main >/dev/null 2>&1; then
  report "$pinned" "unreachable — the corpus's remote main could not be fetched" "(unknown)"
  exit 0
fi
tip=$(git -C "$dir" rev-parse FETCH_HEAD)

if git -C "$dir" merge-base --is-ancestor "$pinned" "$tip" 2>/dev/null; then
  behind=$(git -C "$dir" rev-list --count "$pinned..$tip")
  if [ "$behind" = 0 ]; then
    state="at the corpus's merged main"
  else
    state="behind the corpus's merged main by $behind commit(s) — an advance available NOW (a regeneration PR that bumps the pin)"
  fi
else
  state="not an ancestor of the corpus's merged main — a divergence, not an advance"
fi

report "$pinned" "$state" "$tip"
exit 0
