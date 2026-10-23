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
# THE STATES ARE THE PIN CONTRACT'S (umbrella AGENTS.md Part II rule 3): `cur`,
# `behind` and `not-on-the-served-line` — the three a recorded corpus pin can be
# in against the corpus's merged main. A corpus is squash-merged, so a pin that is
# off the corpus's main line is a SQUASH-ADVANCE — `not-on-the-served-line` —
# whose one remedy is the same as `behind`'s: the consumer re-pins to the tip. It
# is NOT a divergence, and this report never calls it one. Two states of its own
# cover the cases it refuses to guess: `undecidable` (the corpus's history could
# not be deepened, so ancestry cannot be judged) and `unreadable` (the pin, or the
# corpus's merged main, could not be read).
#
# The producer-side half of the same question lives in opencharly/marketplace
# (`scripts/consumer-currency.sh`) and speaks the SAME vocabulary, state for
# state, so a reader sees one language on both sides of the pin. The two differ
# in where they stand, and that difference is deliberate: the producer judges
# from the corpus's OWN history and refuses to judge a shallow one, while this
# report judges from the consumer's checkout and DEEPENS it first (below) — the
# corpus's history is small, so the corpus-side answer is available instead of
# merely declared unavailable.
#
# THE JUDGMENT MUST BE DECIDABLE BEFORE IT IS REPORTED. `merge-base
# --is-ancestor` answers "not an ancestor" for a commit the clone does not have,
# which is indistinguishable from a real squash-advance — and the checkout of
# this submodule in CI IS a depth-1 clone: actions/checkout runs `git submodule
# update --init --force --depth=<fetch-depth>` with its default `fetch-depth: 1`
# (actions/checkout@v7, `src/git-command-manager.ts`, `submoduleUpdate`). A
# depth-1 history therefore cannot judge ancestry at all, and reporting from it
# would state a FALSE state — a divergence for a pin that is merely behind, with
# a wrong commit count. So a shallow corpus is DEEPENED first, and when the
# deepening cannot be done the report says `undecidable` and never guesses: a
# false state is worse than no report.
#
# Usage: check_corpus_currency.sh <superproject-root> [<corpus-dir>]
# Prints exactly one line:
#   corpus pin: <pinned> is <state> (merged main: <tip>)
# Exit status is 0 in EVERY state, including a squash-advance, an undecidable
# history and a missing corpus: a report that could fail the build would be a
# gate, and this is not one.
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
  report "(no pin)" "unreadable — the superproject records no gitlink for '$corpus'" "(unknown)"
  exit 0
fi

if ! git -C "$dir" rev-parse --verify -q HEAD >/dev/null 2>&1; then
  report "$pinned" "unreadable — the corpus has no checkout here, so its merged main could not be read" "(unknown)"
  exit 0
fi

# The corpus's merged main, as the remote sees it right now. The fetch brings
# the tip's objects in, so the ancestry test below is decidable rather than
# unanswerable.
shallow=no
if [ "$(git -C "$dir" rev-parse --is-shallow-repository 2>/dev/null)" = "true" ]; then
  shallow=yes
fi

if [ "$shallow" = yes ]; then
  # The history is too short to answer the question, so it is completed first.
  # If it cannot be completed, the question is NOT answered — it is reported as
  # undecidable.
  if ! git -C "$dir" fetch --quiet --unshallow origin main >/dev/null 2>&1; then
    report "$pinned" "undecidable — the corpus's history is shallow and could not be deepened, so ancestry cannot be judged" "(unknown)"
    exit 0
  fi
else
  if ! git -C "$dir" fetch --quiet origin main >/dev/null 2>&1; then
    report "$pinned" "unreadable — the corpus's remote main could not be fetched" "(unknown)"
    exit 0
  fi
fi
tip=$(git -C "$dir" rev-parse FETCH_HEAD)

if git -C "$dir" merge-base --is-ancestor "$pinned" "$tip" 2>/dev/null; then
  behind=$(git -C "$dir" rev-list --count "$pinned..$tip")
  if [ "$behind" = 0 ]; then
    state="cur — at the corpus's merged main"
  else
    state="behind — $behind commit(s) behind the corpus's merged main; an advance available NOW (a pin-bump PR in this repo)"
  fi
else
  state="not-on-the-served-line — the pin is not on the corpus's main line; its one remedy is the same as behind's (a pin-bump PR in this repo), and it is not a divergence"
fi

report "$pinned" "$state" "$tip"
exit 0
