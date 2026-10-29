#!/usr/bin/env bash
# check_pin_currency.sh — REPORT the currency of every SOURCE PIN the site consumes.
# It never fails.
#
# WHY THIS EXISTS. The site is generated from THREE pinned inputs: the guidance
# corpus (this repo's `marketplace` gitlink), the `charly` commit the deploy
# clones, and the umbrella commit the deploy clones. Every one of them is
# advanced by a MANUAL act after its producer lands, so the site trails its
# producers by however long nobody ran the regeneration — and the drift gate
# CANNOT see it: the PINNED sources regenerate their own (old) pages perfectly,
# so a stale pin is invisible to it. The drift gate answers "does the committed
# content match what the pinned inputs generate?" (yes, always); this answers the
# second question — "is each pinned input itself current?".
#
# THE ANSWER IS REPORTED, NEVER FAILED. A pin that is behind is an advance
# available NOW — the same shape the pin contract calls `behind`: a reportable
# state, not a broken edge. A gate that FAILED on it would be red on every push
# until somebody ran the regeneration PR, and the remedy is that PR, not a gate.
#
# THE STATES ARE THE PIN CONTRACT'S (umbrella AGENTS.md Part II rule 3): `cur`,
# `behind` and `not-on-the-served-line` — the three a recorded pin can be in
# against its producer's merged main. A pin that is off the producer's main line
# is a SQUASH-ADVANCE — `not-on-the-served-line` — whose one remedy is the same
# as `behind`'s: the consumer re-pins to the tip. It is NOT a divergence, and
# this report never calls it one. Two states of its own cover the cases it
# refuses to guess: `undecidable` (the history could not be deepened, so
# ancestry cannot be judged) and `unreadable` (the pin, or the producer's
# merged main, could not be read).
#
# The producer-side half of the same question lives in opencharly/marketplace
# (`scripts/consumer-currency.sh`) and speaks the SAME vocabulary, state for
# state, so a reader sees one language on both sides of the pin.
#
# THE JUDGMENT MUST BE DECIDABLE BEFORE IT IS REPORTED. `merge-base
# --is-ancestor` answers "not an ancestor" for a commit the clone does not have,
# which is indistinguishable from a real squash-advance — and the corpus
# checkout of this submodule in CI IS a depth-1 clone: actions/checkout runs
# `git submodule update --init --force --depth=<fetch-depth>` with its default
# `fetch-depth: 1` (actions/checkout@v7, `src/git-command-manager.ts`,
# `submoduleUpdate`). A depth-1 history therefore cannot judge ancestry at all,
# and reporting from it would state a FALSE state — a divergence for a pin that
# is merely behind, with a wrong commit count. So a shallow history is
# DEEPENED first, and when the deepening cannot be done the report says
# `undecidable` and never guesses: a false state is worse than no report. The
# same rule covers a pin whose commit is not in the history at all: the report
# says `unreadable`, because "not an ancestor" and "not here" are different
# facts and only one of them is a state.
#
# THE REPORT IS SELF-CONTAINED. It answers the question from THIS repository's
# own records — the committed corpus gitlink and the CI-time pins the workflow
# records — and reads each producer's history itself. It does not depend on the
# deploy's own checkouts, on where they live, or on the order the workflow
# happens to run its steps in: a control that reads another step's private state
# is a control that breaks when the step moves.
#
# THE PINS ARE RECORDED ONCE. The two CI-time pins live in the workflow's own
# `env:` block, which the deploy's clone step consumes and this report reads —
# one record, one occurrence of each SHA in the whole repository. The corpus
# pin is the committed gitlink the deploy checks out, and it is read from the
# commit's tree rather than from the checkout's HEAD: the checkout is a
# convenience, the tree entry is the pin.
#
# THE SCOPE IS THE SITE'S THREE SOURCE PINS, and the scope is stated here so a
# reader never has to guess it. The site also consumes RELEASE-TAG pins — the
# generator's own tag, and the per-plugin tags in the corpus wiring candy's
# pins file. Those are a DIFFERENT class of pin: their currency question is
# "is there a newer RELEASE?", not "is this commit behind the producer's
# merged main?", and the org has not given that question a state
# (opencharly/opencharly#793). So they are NAMED, MEASURED and FILED, not
# silently omitted — a pin that is invisible is the defect this report exists
# to end, and it does not end it by pretending a tag is a commit.
#
# Usage: check_pin_currency.sh [<superproject-root> [<corpus-dir>]]
# Prints one line per pin:
#   <producer> pin: <pinned> is <state> (merged main: <tip>)
# Exit status is 0 in EVERY state, including a squash-advance, an undecidable
# history and a missing pin: a report that could fail the build would be a
# gate, and this is not one.
set -u

root=${1:-.}
corpus=${2:-marketplace}
workflow="$root/.github/workflows/deploy.yml"

report() {
  echo "$1 pin: $2 is $3 (merged main: $4)"
}

# The name each producer is called BY in a sentence. "the corpus" and "the
# umbrella" are common nouns and need their article; "charly" is a name and
# does not. The corpus's line is worded exactly as the corpus-only report
# worded it, so a reader who knows the old line reads the same words here.
producer_label() {
  case "$1" in
    corpus | umbrella) echo "the $1" ;;
    *) echo "$1" ;;
  esac
}

# The value of one key of the workflow's own `env:` block — where the CI-time
# pins are recorded. An absent block, an absent key and an unreadable file all
# yield the empty string, which the callers report as `unreadable`.
#
# The value is everything after the key's colon, trimmed, with one layer of
# surrounding quotes removed: the block is YAML, and YAML may quote a value.
workflow_value() {
  [ -f "$workflow" ] || return 0
  awk -v key="$1" '
    /^env:[[:space:]]*$/ { in_env = 1; next }
    {
      if (!in_env) next
      if ($0 ~ /^[^[:space:]#]/) { in_env = 0; next }
      line = $0
      sub(/^[[:space:]]+/, "", line)
      if (index(line, key ":") != 1) next
      v = substr(line, length(key) + 2)
      gsub(/^[[:space:]]+|[[:space:]]+$/, "", v)
      gsub(/^"|"$/, "", v)
      gsub(/^\047|\047$/, "", v)
      print v
      exit
    }
  ' "$workflow" 2>/dev/null
}

# judge <producer> <pin> <checkout-dir>
#
# The checkout must be a git repository with an `origin` remote. The judgement
# is made against the producer's merged main AS THE REMOTE SERVES IT NOW, so
# the fetch happens before the question is asked, and the question is asked
# only from a history that can answer it.
judge() {
  local producer=$1 pin=$2 dir=$3
  local label tip behind state shallow

  label=$(producer_label "$producer")

  if ! git -C "$dir" cat-file -e "$pin^{commit}" 2>/dev/null; then
    report "$producer" "$pin" \
      "unreadable — the pinned commit is not in $label's history, so its merged main could not be compared" \
      "(unknown)"
    return 0
  fi

  shallow=no
  if [ "$(git -C "$dir" rev-parse --is-shallow-repository 2>/dev/null)" = "true" ]; then
    shallow=yes
  fi

  if [ "$shallow" = yes ]; then
    # The history is too short to answer the question, so it is completed first.
    # If it cannot be completed, the question is NOT answered — it is reported
    # as undecidable.
    if ! git -C "$dir" fetch --quiet --unshallow origin main >/dev/null 2>&1; then
      report "$producer" "$pin" \
        "undecidable — $label's history is shallow and could not be deepened, so ancestry cannot be judged" \
        "(unknown)"
      return 0
    fi
  else
    if ! git -C "$dir" fetch --quiet origin main >/dev/null 2>&1; then
      report "$producer" "$pin" \
        "unreadable — $label's remote main could not be fetched" "(unknown)"
      return 0
    fi
  fi

  tip=$(git -C "$dir" rev-parse FETCH_HEAD)

  if git -C "$dir" merge-base --is-ancestor "$pin" "$tip" 2>/dev/null; then
    behind=$(git -C "$dir" rev-list --count "$pin..$tip")
    if [ "$behind" = 0 ]; then
      state="cur — at $label's merged main"
    else
      state="behind — $behind commit(s) behind $label's merged main; an advance available NOW (a pin-bump PR in this repo)"
    fi
  else
    state="not-on-the-served-line — the pin is not on $label's main line; its one remedy is the same as behind's (a pin-bump PR in this repo), and it is not a divergence"
  fi

  report "$producer" "$pin" "$state" "$tip"
}

# ── the corpus gitlink ─────────────────────────────────────────────────────────
# The pin is the COMMITTED gitlink — the tree entry the deploy checks out —
# not the checkout's HEAD. A checkout that is not at the pin is a different
# question (and the drift gate asks it).
if ! pinned=$(git -C "$root" rev-parse --verify -q "HEAD:$corpus" 2>/dev/null); then
  report "corpus" "(no pin)" \
    "unreadable — the superproject records no gitlink for '$corpus'" "(unknown)"
elif ! git -C "$root/$corpus" rev-parse --verify -q HEAD >/dev/null 2>&1; then
  report "corpus" "$pinned" \
    "unreadable — the corpus has no checkout here, so its merged main could not be read" \
    "(unknown)"
else
  judge "corpus" "$pinned" "$root/$corpus"
fi

# ── the CI-time source pins ───────────────────────────────────────────────────
# Each producer is read from the workflow's own `env:` block and judged against
# a checkout this report makes itself, so the judgement never depends on what
# the deploy happened to clone, or on where it put it.
tmp=$(mktemp -d)
trap 'rm -rf "$tmp"' EXIT

for producer in charly umbrella; do
  upper=$(printf '%s' "$producer" | tr '[:lower:]' '[:upper:]')
  label=$(producer_label "$producer")
  pin=$(workflow_value "${upper}_PIN")
  url=$(workflow_value "${upper}_REPO")
  if [ -z "$pin" ] || [ -z "$url" ]; then
    report "$producer" "${pin:-(no pin)}" \
      "unreadable — $label's pin is not recorded in $workflow" "(unknown)"
    continue
  fi
  dir="$tmp/$producer"
  # A blobless clone — every commit and tree, no blobs: enough to judge
  # ancestry, cheap enough to run on every push. NOT `--single-branch`: a pin
  # that is off the producer's main line is a real state
  # (`not-on-the-served-line`), and a single-branch clone would not hold that
  # commit at all, so the report could not tell "off the line" from "not here".
  if ! git clone --quiet --filter=blob:none --no-checkout "$url" "$dir" >/dev/null 2>&1; then
    report "$producer" "$pin" \
      "unreadable — $label's repository could not be cloned, so its merged main could not be read" \
      "(unknown)"
    continue
  fi
  judge "$producer" "$pin" "$dir"
done

exit 0
