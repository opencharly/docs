#!/usr/bin/env bash
# test_check_corpus_currency.sh — prove the currency REPORT is right, on fixtures.
#
# The report is the control that stops the NEXT drift: the drift gate cannot see a
# stale corpus (the pinned corpus regenerates its own old pages perfectly), so the
# workflow asks the second question and answers it. A report nobody checked is a
# comment, so every state the report can name is built here as a fixture and
# asserted EXACTLY:
#
#   1. the pin is at the corpus's merged main      -> "at the corpus's merged main"
#   2. the pin is one commit behind it             -> "behind ... by 1 commit(s)"
#   3. the pin is not an ancestor of it (diverged) -> "a divergence, not an advance"
#   4. the corpus has no checkout here             -> "not materialized"
#
# And the property that makes the report a report and NOT a gate: it exits 0 in
# EVERY case, including the divergence. A report that could fail a build would be a
# gate, and gating here would be red on every push until somebody ran the
# regeneration PR.
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

# A corpus origin with one commit on main and a divergent line on side.
mk_corpus() {
  local base=$1
  mkdir -p "$base/work"
  git init --quiet -b main "$base/work"
  git -C "$base/work" config user.email test@example.invalid
  git -C "$base/work" config user.name test
  echo one >"$base/work/f"
  git -C "$base/work" add f
  git -C "$base/work" commit -qm one
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

# ── 1. the pin is at the corpus's merged main ──────────────────────────────────────
base="$tmp/a"
mk_corpus "$base"
one=$(git -C "$base/work" rev-parse main)
mk_super "$tmp/a/super" "$one"
git clone --quiet -b main "$base/origin.git" "$tmp/a/super/marketplace"
out=$(run_report "$tmp/a/super")
rc=$?
assert_state "the pin is at the corpus's merged main" \
  "is at the corpus's merged main (merged main: $one)" "$out" "$rc"

# ── 2. the pin is one commit behind the corpus's merged main ──────────────────────
base="$tmp/b"
mk_corpus "$base"
one=$(git -C "$base/work" rev-parse main)
echo two >"$base/work/h"
git -C "$base/work" add h
git -C "$base/work" commit -qm advance
git -C "$base/work" push -q origin main
mk_super "$tmp/b/super" "$one"
git clone --quiet -b main "$base/origin.git" "$tmp/b/super/marketplace"
out=$(run_report "$tmp/b/super")
rc=$?
assert_state "the pin is one commit behind" \
  "is behind the corpus's merged main by 1 commit(s)" "$out" "$rc"

# ── 3. the pin is not an ancestor of the corpus's merged main ─────────────────────
base="$tmp/c"
mk_corpus "$base"
side=$(git -C "$base/work" rev-parse side)
mk_super "$tmp/c/super" "$side"
git clone --quiet -b main "$base/origin.git" "$tmp/c/super/marketplace"
out=$(run_report "$tmp/c/super")
rc=$?
assert_state "the pin diverged from the corpus's merged main" \
  "is not an ancestor of the corpus's merged main — a divergence, not an advance" "$out" "$rc"

# ── 4. the corpus has no checkout here ───────────────────────────────────────────
base="$tmp/d"
mk_corpus "$base"
one=$(git -C "$base/work" rev-parse main)
mk_super "$tmp/d/super" "$one"
out=$(run_report "$tmp/d/super")
rc=$?
assert_state "the corpus is not materialized" \
  "is not materialized — the corpus has no checkout here" "$out" "$rc"

if [ "$fails" -ne 0 ]; then
  echo "test_check_corpus_currency: FAIL ($fails)"
  exit 1
fi
echo "test_check_corpus_currency: OK (every state is reported, and none of them fails)"
exit 0
