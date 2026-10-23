#!/usr/bin/env bash
# test_check_corpus_currency.sh — prove the currency REPORT is right, on fixtures.
#
# The report is the control that stops the NEXT drift: the drift gate cannot see a
# stale corpus (the pinned corpus regenerates its own old pages perfectly), so the
# workflow asks the second question and answers it. A report nobody checked is a
# comment, so every state the report can name is built here as a fixture and
# asserted EXACTLY:
#
#   1. the pin is at the corpus's merged main      -> "cur — at the corpus's merged main"
#   2. the pin is behind it                        -> "behind — N commit(s) behind ..."
#   3. the pin is not on the corpus's main line    -> "not-on-the-served-line ..."
#   4. the corpus has no checkout here             -> "unreadable — ..."
#   5. the superproject records no gitlink         -> "unreadable — ... no gitlink ..."
#   6. the corpus's remote main cannot be fetched  -> "unreadable — ..."
#   7. the corpus's history is shallow and cannot
#      be deepened                                  -> "undecidable — ..."
#   8. the corpus is a DEPTH-1 checkout at a pin
#      that IS behind — the shape CI has            -> "behind — 2 commit(s) ..."
#
# Fixture 8 is the one that earns the rest: a depth-1 history cannot answer the
# ancestry question, so a report that judged from it would state a FALSE state — a
# divergence for a pin that is merely behind, with a wrong commit count. The
# checkout in CI IS a depth-1 clone (actions/checkout's `submodule update
# --depth=<fetch-depth>`, default 1), so this fixture is the CI shape, and the
# report must answer it truthfully.
#
# And the property that makes the report a report and NOT a gate: it exits 0 in
# EVERY case, including the squash-advance. A report that could fail a build
# would be a gate, and gating here would be red on every push until somebody ran
# the regeneration PR.
set -u

here=$(cd "$(dirname "$0")" && pwd)
script="$here/check_corpus_currency.sh"
tmp=$(mktemp -d)
trap 'rm -rf "$tmp"' EXIT
fails=0

pass() { echo "  PASS  $1"; }
fail() {
  fails=$((fails + 1))
  echo "  FAIL  $1"
}

# A corpus origin with $2 commits on main (>= 1) and a divergent line on side.
mk_corpus() {
  local base=$1 n=$2 i
  mkdir -p "$base/work"
  git init --quiet -b main "$base/work"
  git -C "$base/work" config user.email test@example.invalid
  git -C "$base/work" config user.name test
  for i in $(seq 1 "$n"); do
    echo "$i" >"$base/work/f$i"
    git -C "$base/work" add "f$i"
    git -C "$base/work" commit -qm "commit $i"
  done
  git init --quiet --bare "$base/origin.git"
  # the bare origin's HEAD must name the branch the corpus publishes on, or a
  # clone of it checks out nothing
  git -C "$base/origin.git" symbolic-ref HEAD refs/heads/main
  git -C "$base/work" remote add origin "$base/origin.git"
  git -C "$base/work" push -q origin main
  git -C "$base/work" checkout -q -b side
  echo two >"$base/work/g"
  git -C "$base/work" add g
  git -C "$base/work" commit -qm side
  git -C "$base/work" push -q origin side
  git -C "$base/work" checkout -q main
}

# A superproject whose `marketplace` gitlink records the given commit.
mk_super() {
  local dir=$1 sha=$2
  mkdir -p "$dir"
  git init --quiet -b main "$dir"
  git -C "$dir" config user.email test@example.invalid
  git -C "$dir" config user.name test
  git -C "$dir" update-index --add --cacheinfo "160000,$sha,marketplace"
  git -C "$dir" commit -qm pin
}

# A superproject that records NO gitlink at all.
mk_super_without_pin() {
  local dir=$1
  mkdir -p "$dir"
  git init --quiet -b main "$dir"
  git -C "$dir" config user.email test@example.invalid
  git -C "$dir" config user.name test
  echo nothing >"$dir/readme"
  git -C "$dir" add readme
  git -C "$dir" commit -qm none
}

# A DEPTH-1 checkout of the corpus, sitting at $2 — the shape CI has.
# `file://` is required: a local-path clone ignores --depth.
mk_shallow_checkout() {
  local base=$1 pin=$2 out=$3
  git clone --quiet --depth 1 -b main "file://$base/origin.git" "$out"
  git -C "$out" fetch --quiet --depth 1 origin "$pin"
  git -C "$out" checkout --quiet "$pin"
}

run_report() { # $1 = superproject dir; prints the report, returns its exit code
  local out rc
  out=$(bash "$script" "$1" 2>&1)
  rc=$?
  echo "$out"
  return $rc
}

assert_state() { # $1 label, $2 expected substring, $3 actual output, $4 exit code
  case "$3" in
    *"$2"*) pass "$1" ;;
    *)
      fail "$1 — the report does not name the expected state"
      echo "        expected to contain: $2"
      echo "        got: $3"
      ;;
  esac
  if [ "$4" = 0 ]; then
    pass "$1 — the report exits 0 (a report must never fail the build)"
  else
    fail "$1 — the report exited $4; it must exit 0 in every state"
  fi
}

# The report must NEVER name a state the pin contract does not have. The retired
# wording called a squash-advance a "divergence" and sent the reader after the
# wrong remedy: the corpus is squash-merged, so a pin off the main line is a
# SQUASH-ADVANCE whose remedy is the same as `behind`'s. The fragments below are
# the instrument that detects the retired sentences; the retired sentences
# themselves live only in the pre-change tree, and the repo-wide sweep in the
# PR body greps for them and finds none.
assert_not_divergence() { # $1 label, $2 output
  case "$2" in
    *"divergence, not an advance"* | *"not an ancestor"*)
      fail "$1 — the report still names the retired divergence wording"
      echo "        got: $2"
      ;;
    *) pass "$1 — the report does not call a squash-advance a divergence" ;;
  esac
}

# ── 1. the pin is at the corpus's merged main ──────────────────────────────────────
base="$tmp/a"
mk_corpus "$base" 1
one=$(git -C "$base/work" rev-parse main)
mk_super "$tmp/a/super" "$one"
git clone --quiet -b main "$base/origin.git" "$tmp/a/super/marketplace"
out=$(run_report "$tmp/a/super")
rc=$?
assert_state "the pin is at the corpus's merged main" \
  "is cur — at the corpus's merged main (merged main: $one)" "$out" "$rc"
assert_not_divergence "the pin is at the corpus's merged main" "$out"

# ── 2. the pin is one commit behind the corpus's merged main ──────────────────────
base="$tmp/b"
mk_corpus "$base" 2
one=$(git -C "$base/work" rev-parse main~1)
mk_super "$tmp/b/super" "$one"
git clone --quiet -b main "$base/origin.git" "$tmp/b/super/marketplace"
out=$(run_report "$tmp/b/super")
rc=$?
assert_state "the pin is one commit behind" \
  "is behind — 1 commit(s) behind the corpus's merged main" "$out" "$rc"
assert_not_divergence "the pin is one commit behind" "$out"

# ── 3. the pin is not on the corpus's main line (a squash-advance) ─────────────────
base="$tmp/c"
mk_corpus "$base" 1
side=$(git -C "$base/work" rev-parse side)
mk_super "$tmp/c/super" "$side"
git clone --quiet -b main "$base/origin.git" "$tmp/c/super/marketplace"
out=$(run_report "$tmp/c/super")
rc=$?
assert_state "the pin is off the corpus's main line" \
  "is not-on-the-served-line — the pin is not on the corpus's main line" "$out" "$rc"
assert_not_divergence "the pin is off the corpus's main line" "$out"

# ── 4. the corpus has no checkout here ───────────────────────────────────────────
base="$tmp/d"
mk_corpus "$base" 1
one=$(git -C "$base/work" rev-parse main)
mk_super "$tmp/d/super" "$one"
out=$(run_report "$tmp/d/super")
rc=$?
assert_state "the corpus is not materialized" \
  "is unreadable — the corpus has no checkout here" "$out" "$rc"

# ── 5. the superproject records no gitlink ───────────────────────────────────────
out=$(run_report "$tmp/e/super")
rc=$?
assert_state "the superproject records no corpus pin" \
  "is unreadable — the superproject records no gitlink for 'marketplace'" "$out" "$rc"
mk_super_without_pin "$tmp/e/super"
out=$(run_report "$tmp/e/super")
rc=$?
assert_state "the superproject records no corpus pin" \
  "is unreadable — the superproject records no gitlink for 'marketplace'" "$out" "$rc"

# ── 6. the corpus's remote main cannot be fetched ─────────────────────────────────
base="$tmp/f"
mk_corpus "$base" 1
one=$(git -C "$base/work" rev-parse main)
mk_super "$tmp/f/super" "$one"
git clone --quiet -b main "$base/origin.git" "$tmp/f/super/marketplace"
# the remote is gone: the fetch of the corpus's merged main must fail
git -C "$tmp/f/super/marketplace" remote set-url origin "$tmp/f/gone.git"
out=$(run_report "$tmp/f/super")
rc=$?
assert_state "the corpus's remote main cannot be fetched" \
  "is unreadable — the corpus's remote main could not be fetched" "$out" "$rc"

# ── 7. the corpus's history is shallow and cannot be deepened ─────────────────────
base="$tmp/g"
mk_corpus "$base" 2
one=$(git -C "$base/work" rev-parse main)
mk_super "$tmp/g/super" "$one"
mk_shallow_checkout "$base" "$one" "$tmp/g/super/marketplace"
git -C "$tmp/g/super/marketplace" remote set-url origin "$tmp/g/gone.git"
out=$(run_report "$tmp/g/super")
rc=$?
assert_state "the corpus's history is shallow and cannot be deepened" \
  "is undecidable — the corpus's history is shallow and could not be deepened" "$out" "$rc"

# ── 8. the corpus is a DEPTH-1 checkout at a pin that IS behind ───────────────────
# The CI shape. The pin is an ancestor of the corpus's merged main, so the report
# must say `behind` with the TRUE commit count — not a divergence, and not the
# wrong count a depth-1 history produces.
base="$tmp/h"
mk_corpus "$base" 3
one=$(git -C "$base/work" rev-parse main~2)
mk_super "$tmp/h/super" "$one"
mk_shallow_checkout "$base" "$one" "$tmp/h/super/marketplace"
out=$(run_report "$tmp/h/super")
rc=$?
assert_state "the corpus is a depth-1 checkout at a pin that is behind" \
  "is behind — 2 commit(s) behind the corpus's merged main" "$out" "$rc"
assert_not_divergence "the corpus is a depth-1 checkout at a pin that is behind" "$out"

if [ "$fails" -ne 0 ]; then
  echo "test_check_corpus_currency: FAIL ($fails)"
  exit 1
fi
echo "test_check_corpus_currency: OK (every state is reported, and none of them fails)"
exit 0
