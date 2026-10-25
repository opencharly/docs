#!/usr/bin/env python3
"""Require every workflow step and every job in this repo to carry a deadline.

WHY. A GitHub Actions step with no `timeout-minutes` has no bound of its own:
if the command it runs hangs -- a clone that never finishes, a generator waiting
on a lock, a network call with no response -- the step runs until the runner's
own limit (six hours) and the job never reports WHICH step died. A step bound
turns that stall into a time-bounded failure that NAMES the step it died in; a
job bound turns the whole job's stall into a failure with a total deadline.

This repo's deploy workflow had no bound on any of its sixteen steps and no
total deadline on its job (opencharly/docs#162), and the tag-on-merge
dispatcher had none either, so the rule is enforced here, on the workflows of
this repo.

NO YAML PARSER, ON PURPOSE. The docs site carries no YAML dependency
(package.json: astro, starlight, sharp, wrangler), and a check that needs a
package the repo does not carry is a check that does not run. The scanner below
is an indentation reader for the shape GitHub Actions defines, and the
self-test proves it against fixtures -- including the trap a grep falls into: a
`timeout-minutes:` that appears inside a `run:` block is TEXT, not a key, and
must not satisfy the rule.
"""

from pathlib import Path
import re
import sys

ROOT = Path(__file__).resolve().parent.parent.parent
WORKFLOW_DIR = ROOT / ".github" / "workflows"

# A mapping key: its own indentation, its name, and whatever follows the colon.
KEY_RE = re.compile(r"^(?P<indent>[ \t]*)(?P<key>[A-Za-z0-9_.\-]+):(?P<rest>[ ].*|)$")
# A block-scalar header: `|`, `>`, with the usual chomping/indent indicators.
BLOCK_RE = re.compile(r"^[|>][-+]?\d*$")
# A timeout value: an integer, optionally followed by a comment.
TIMEOUT_RE = re.compile(r"^(?P<value>\d+)\s*(#.*)?$")
# GitHub's own ceiling for both job and step timeouts.
MAX_TIMEOUT = 360
# The keys that label a step when it has no `name:`.
LABEL_KEYS = ("name", "uses", "run")


def _commented_out(value: str) -> str:
    """The value with a trailing `# comment` removed.

    Only ever applied to a value that is a bare scalar (a number, or a block
    header), where a `#` cannot be inside a quoted string.
    """
    return value.split("#", 1)[0].strip()


def _mark_block_scalars(lines: list[str]) -> list[bool]:
    """Mark every line that is CONTENT of a block scalar, not YAML structure.

    A `run: |` step body is a shell script, not a mapping: a line inside it
    that looks like `timeout-minutes: 10` is text the shell would see, and a
    step whose only "timeout" is inside such a body is UNBOUND. The content of
    a block scalar is every following line indented deeper than its key.
    """
    skip = [False] * len(lines)
    index = 0
    while index < len(lines):
        line = lines[index]
        stripped = line.strip()
        if not stripped or stripped.startswith("#"):
            index += 1
            continue
        match = KEY_RE.match(line)
        if not match:
            index += 1
            continue
        key_indent = len(match.group("indent"))
        if not BLOCK_RE.match(_commented_out(match.group("rest"))):
            index += 1
            continue
        # A block scalar: swallow the deeper-indented body that follows.
        cursor = index + 1
        while cursor < len(lines):
            body = lines[cursor]
            if not body.strip():
                skip[cursor] = True
                cursor += 1
                continue
            if len(body) - len(body.lstrip()) > key_indent:
                skip[cursor] = True
                cursor += 1
                continue
            break
        index = cursor
    return skip


def _structure(lines: list[str]) -> tuple[list[tuple[int, int, str, str]], list[tuple[int, int, str]]]:
    """The mapping keys and the list items of a workflow, with their columns.

    Returns (keys, items) where a key is (line index, column, name, value) and
    an item is (line index, column, text) -- a `- ` list entry.
    """
    skip = _mark_block_scalars(lines)
    keys: list[tuple[int, int, str, str]] = []
    items: list[tuple[int, int, str]] = []
    for index, line in enumerate(lines):
        if skip[index]:
            continue
        stripped = line.strip()
        if not stripped or stripped.startswith("#"):
            continue
        match = KEY_RE.match(line)
        if match:
            keys.append(
                (
                    index,
                    len(match.group("indent")),
                    match.group("key"),
                    _commented_out(match.group("rest")),
                )
            )
            continue
        if stripped.startswith("- "):
            dash = len(line) - len(line.lstrip())
            text = stripped[2:].strip()
            items.append((index, dash, text))
    return keys, items


def _label_of(text: str) -> str:
    """The human label of a list item: the key it opens with."""
    match = KEY_RE.match(text)
    if not match:
        return text[:60]
    name = match.group("key")
    if name in LABEL_KEYS:
        value = _commented_out(match.group("rest"))
        if name == "run":
            value = value.splitlines()[0] if value else ""
        return f"{name}: {value}" if value else name
    return name


def _timeout_at(keys, start: int, end: int, column: int) -> tuple[bool, str]:
    """Whether a `timeout-minutes:` key sits at `column` between two lines."""
    for index, indent, name, value in keys:
        if index < start or index >= end:
            continue
        if name != "timeout-minutes" or indent != column:
            continue
        match = TIMEOUT_RE.match(value)
        if not match:
            return False, f"timeout-minutes is not a number: {value!r}"
        minutes = int(match.group("value"))
        if minutes < 1 or minutes > MAX_TIMEOUT:
            return False, f"timeout-minutes {minutes} is outside 1..{MAX_TIMEOUT}"
        return True, ""
    return False, ""


def _timeout_minutes(keys, start: int, end: int, column: int) -> int | None:
    """The minutes of the `timeout-minutes:` key at `column`, if it is a valid one."""
    for index, indent, name, value in keys:
        if index < start or index >= end:
            continue
        if name != "timeout-minutes" or indent != column:
            continue
        match = TIMEOUT_RE.match(value)
        if not match:
            return None
        minutes = int(match.group("value"))
        if minutes < 1 or minutes > MAX_TIMEOUT:
            return None
        return minutes
    return None


def check_text(text: str, label: str = "<workflow>") -> list[str]:
    """Every deadline missing from one workflow, as findings."""
    lines = text.splitlines()
    keys, items = _structure(lines)
    findings: list[str] = []

    jobs = [key for key in keys if key[2] == "jobs"]
    if not jobs:
        return findings
    jobs_index, jobs_indent = jobs[0][0], jobs[0][1]

    # The `jobs:` MAPPING ends at the next key at its OWN indent — a top-level
    # `env:` or `on:` after it is a sibling of `jobs:`, not a job. Without this
    # bound, a top-level `env:` child was read as a job and reported missing
    # its deadline, which is a false positive on a perfectly good workflow.
    jobs_end = len(lines)
    for key in keys:
        if key[0] > jobs_index and key[1] <= jobs_indent:
            jobs_end = key[0]
            break

    # A job is a MAPPING key under `jobs:`; the jobs sit at one column and
    # each job's own keys sit one column deeper.
    job_starts = [
        key for key in keys if jobs_index < key[0] < jobs_end and key[1] > jobs_indent
    ]
    if not job_starts:
        return findings
    job_indent = job_starts[0][1]
    job_names = [
        key for key in job_starts if key[1] == job_indent
    ]
    for position, job in enumerate(job_names):
        job_name = job[2]
        job_start = job[0]
        job_end = (
            job_names[position + 1][0] if position + 1 < len(job_names) else jobs_end
        )
        # The job's own key column: the first key deeper than the job's name.
        own = [key for key in keys if job_start < key[0] < job_end and key[1] > job_indent]
        if not own:
            continue
        job_column = own[0][1]
        bounded, why = _timeout_at(keys, job_start, job_end, job_column)
        job_minutes = _timeout_minutes(keys, job_start, job_end, job_column)
        if not bounded:
            reason = why or "the job has no total deadline"
            findings.append(f"{label}: job '{job_name}' {reason}")

        steps = [key for key in own if key[2] == "steps" and key[1] == job_column]
        if not steps:
            continue
        steps_index, steps_indent = steps[0][0], steps[0][1]
        # The step LIST ends at the next key at the job's own column: a job
        # whose `env:` is a list of maps would otherwise have its list items
        # read as steps.
        steps_end = job_end
        for key in keys:
            if key[0] > steps_index and key[1] == job_column:
                steps_end = key[0]
                break
        step_items = [
            item for item in items if steps_index < item[0] < steps_end and item[1] > steps_indent
        ]
        if not step_items:
            continue
        step_indent = step_items[0][1]
        for number, item in enumerate(step_items, start=1):
            if item[1] != step_indent:
                continue
            step_start = item[0]
            # The step ends where the NEXT step begins, or where the job ends.
            # It must not reach past the job: a later job's `timeout-minutes:` is
            # a different step's key, and letting the search run to the end of
            # the file would let it satisfy this step.
            step_end = job_end
            for later in step_items[number:]:
                if later[1] == step_indent:
                    step_end = later[0]
                    break
            # The step's key column: where its first key starts on the dash line.
            step_column = item[1] + 2
            while step_column < len(lines[step_start]) and lines[step_start][step_column] == " ":
                step_column += 1
            bounded, why = _timeout_at(keys, step_start, step_end, step_column)
            if not bounded:
                reason = why or "the step has no deadline"
                findings.append(
                    f"{label}: step {number} ('{_label_of(item[2])}') in job '{job_name}' {reason}"
                )
            # A step's deadline must be SHORTER than its job's, or the job's
            # deadline fires first and the step's is dead: the stall is then
            # reported against the job, which names no step, and the one
            # property a step bound exists for — that the failure SAYS WHICH
            # STEP died — is gone. The step's own message says so, because the
            # step is what fails and names itself.
            step_minutes = _timeout_minutes(keys, step_start, step_end, step_column)
            if step_minutes is not None and job_minutes is not None and step_minutes >= job_minutes:
                findings.append(
                    f"{label}: step {number} ('{_label_of(item[2])}') in job '{job_name}' "
                    f"its deadline ({step_minutes} min) is not shorter than its job's "
                    f"({job_minutes} min), so the job's deadline fires first and the step's is dead"
                )
    return findings


def check_files(paths: list[Path]) -> list[str]:
    findings: list[str] = []
    for path in paths:
        try:
            text = path.read_text(encoding="utf-8")
        except OSError as exc:
            findings.append(f"{path}: cannot be read: {exc}")
            continue
        try:
            label = str(path.relative_to(ROOT))
        except ValueError:
            label = str(path)
        findings.extend(check_text(text, label))
    return findings


def _workflow_paths(arguments: list[str]) -> list[Path]:
    if not arguments:
        return sorted(WORKFLOW_DIR.glob("*.yml")) + sorted(WORKFLOW_DIR.glob("*.yaml"))
    paths: list[Path] = []
    for argument in arguments:
        path = Path(argument)
        if path.is_dir():
            paths.extend(sorted(path.glob("*.yml")) + sorted(path.glob("*.yaml")))
        else:
            paths.append(path)
    return paths


def self_test() -> None:
    """Prove the checker on fixtures -- including the trap a grep falls into."""
    failures: list[str] = []

    def expect(label: str, condition: bool, detail: str = "") -> None:
        if not condition:
            failures.append(f"{label}{': ' + detail if detail else ''}")

    bounded_workflow = """
name: bounded
jobs:
  deploy:
    runs-on: ubuntu-latest
    timeout-minutes: 45
    steps:
      - name: first
        run: echo one
        timeout-minutes: 5
      - uses: actions/checkout@v7
        timeout-minutes: 10
"""
    expect("a fully bounded workflow has no findings", check_text(bounded_workflow) == [],
           str(check_text(bounded_workflow)))

    unbounded_step = """
name: unbounded
jobs:
  deploy:
    runs-on: ubuntu-latest
    timeout-minutes: 45
    steps:
      - name: first
        run: echo one
      - name: second
        run: echo two
        timeout-minutes: 5
"""
    findings = check_text(unbounded_step)
    expect("an unbounded step is reported", len(findings) == 1, str(findings))
    expect("the finding names the step", "step 1 ('name: first')" in findings[0] if findings else False,
           str(findings))
    expect("the finding names the job", "job 'deploy'" in findings[0] if findings else False, str(findings))

    # The TRAP: the only `timeout-minutes:` in the step is inside the shell
    # body. It is text to the shell, not a key -- a grep would accept it.
    trap = """
name: trap
jobs:
  deploy:
    runs-on: ubuntu-latest
    timeout-minutes: 45
    steps:
      - name: first
        run: |
          # timeout-minutes: 5
          echo one
"""
    findings = check_text(trap)
    expect("a timeout inside a run block does NOT satisfy the rule", len(findings) == 1, str(findings))
    expect("the trap's finding names the step", "step 1" in findings[0] if findings else False, str(findings))

    # A job-level bound must not satisfy a step's requirement.
    job_only = """
name: job-only
jobs:
  deploy:
    runs-on: ubuntu-latest
    timeout-minutes: 45
    steps:
      - name: first
        run: echo one
"""
    findings = check_text(job_only)
    expect("a job bound does not bound its steps", len(findings) == 1, str(findings))
    expect("the job-only finding names the step", "step 1" in findings[0] if findings else False, str(findings))

    # A job with no bound of its own.
    job_unbounded = """
name: job-unbounded
jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
      - name: first
        run: echo one
        timeout-minutes: 5
"""
    findings = check_text(job_unbounded)
    expect("a job with no total deadline is reported", len(findings) == 1, str(findings))
    expect("the job finding is about the job", "job 'deploy'" in findings[0] if findings else False,
           str(findings))

    # A reusable-workflow job has no steps and still needs its own deadline.
    reusable = """
name: reusable
jobs:
  tag:
    uses: opencharly/.github/.github/workflows/tag-on-merge.yml@main
    timeout-minutes: 20
"""
    expect("a bounded reusable-workflow job has no findings", check_text(reusable) == [],
           str(check_text(reusable)))

    reusable_unbounded = """
name: reusable-unbounded
jobs:
  tag:
    uses: opencharly/.github/.github/workflows/tag-on-merge.yml@main
"""
    findings = check_text(reusable_unbounded)
    expect("an unbounded reusable-workflow job is reported", len(findings) == 1, str(findings))

    # An out-of-range value is not a deadline.
    out_of_range = """
name: out-of-range
jobs:
  deploy:
    runs-on: ubuntu-latest
    timeout-minutes: 0
    steps:
      - name: first
        run: echo one
        timeout-minutes: 5
"""
    findings = check_text(out_of_range)
    expect("a zero timeout is rejected", len(findings) == 1, str(findings))
    expect("the rejection names the range", "outside 1..360" in findings[0] if findings else False,
           str(findings))

    # A step with no `name:` is labelled by its `uses:`.
    unnamed = """
name: unnamed
jobs:
  deploy:
    runs-on: ubuntu-latest
    timeout-minutes: 45
    steps:
      - uses: actions/checkout@v7
"""
    findings = check_text(unnamed)
    expect("an unnamed step is labelled by its uses", "uses: actions/checkout@v7" in findings[0] if findings else False,
           str(findings))

    # A top-level `env:` is a SIBLING of `jobs:`, not a job. A checker that
    # reads the `jobs:` mapping as "everything until the end of the file"
    # reports `env:`'s child as a job with no deadline — a false positive on a
    # perfectly good workflow.
    #
    # The sibling must come AFTER the `jobs:` mapping: that is the only
    # position where the end of the mapping is decided, and a sibling BEFORE
    # `jobs:` is excluded by the mapping's own start. A fixture that put it
    # before would pass whatever the end bound did, and prove nothing.
    sibling_env = """
name: sibling-env
jobs:
  deploy:
    runs-on: ubuntu-latest
    timeout-minutes: 45
    steps:
      - name: only
        run: echo one
        timeout-minutes: 5
env:
  FOO:
    BAR: baz
"""
    expect("a top-level env: is not a job", check_text(sibling_env) == [], str(check_text(sibling_env)))

    # A block scalar's BODY is text, not structure. The body of a job-level
    # `env:` map whose value is a block scalar lands on the STEP's own key
    # column, so a reader that does not know the body is text finds
    # "timeout-minutes" there and calls the step bounded. It is not: the step
    # carries no deadline of its own, and it must be reported.
    #
    # This fixture is the one that earns the block-scalar marking. The trap
    # above does not: a `run:` body is indented deeper than the step's keys,
    # so the COLUMN test alone rejects it. This shape puts the body on the
    # step's own column, where only the marking can reject it.
    block_body = """
name: block-body
jobs:
  deploy:
    runs-on: ubuntu-latest
    timeout-minutes: 45
    steps:
      - name: only
        run: echo one
    env:
      NOTE: |
        timeout-minutes: 5
"""
    findings = check_text(block_body)
    expect("a block scalar's body is not a deadline", len(findings) == 1, str(findings))
    expect("the block-body finding names the step", "step 1" in findings[0] if findings else False,
           str(findings))

    # A block scalar's body is not a job either: a `fake-job:` inside a
    # top-level block scalar is text, and the workflow it sits in is not
    # broken by it.
    block_body_is_not_a_job = """
name: block-body-is-not-a-job
x-note: |
  fake-job:
    name: not a job
jobs:
  deploy:
    runs-on: ubuntu-latest
    timeout-minutes: 45
    steps:
      - name: only
        run: echo one
        timeout-minutes: 5
"""
    expect("a block scalar's body is not a job", check_text(block_body_is_not_a_job) == [],
           str(check_text(block_body_is_not_a_job)))

    # A LATER job's step deadline must not satisfy an EARLIER job's last step.
    # The step's search must stop at the end of its own job: a step key that
    # belongs to the next job is a different step's key. (This is the shape
    # that made this checker under-report, and it was found by cross-checking
    # against a real YAML parser over the org's own workflows.)
    cross_job = """
name: cross-job
jobs:
  first:
    runs-on: ubuntu-latest
    timeout-minutes: 45
    steps:
      - name: only
        run: echo one
  second:
    runs-on: ubuntu-latest
    timeout-minutes: 45
    steps:
      - name: later
        run: echo two
        timeout-minutes: 5
"""
    findings = check_text(cross_job)
    expect("a later job's deadline does not satisfy an earlier job's step", len(findings) == 1, str(findings))
    expect("the cross-job finding names the first job's step",
           "step 1 ('name: only') in job 'first'" in findings[0] if findings else False, str(findings))

    # A step's deadline must be SHORTER than its job's. If it is not, the
    # job's deadline fires first and the step's is dead: the stall is
    # reported against the job, which names no step — and naming the step is
    # the one property a step bound exists for.
    dead_step_bound = """
name: dead-step-bound
jobs:
  deploy:
    runs-on: ubuntu-latest
    timeout-minutes: 10
    steps:
      - name: only
        run: echo one
        timeout-minutes: 10
"""
    findings = check_text(dead_step_bound)
    expect("a step bound that is not shorter than its job's is reported",
           len(findings) == 1, str(findings))
    expect("the dead-bound finding says the step's deadline is dead",
           "is dead" in findings[0] if findings else False, str(findings))

    # A step bound SHORTER than the job's is fine: the step is what fails,
    # and it names itself.
    live_step_bound = """
name: live-step-bound
jobs:
  deploy:
    runs-on: ubuntu-latest
    timeout-minutes: 45
    steps:
      - name: only
        run: echo one
        timeout-minutes: 10
"""
    expect("a step bound shorter than its job's is fine",
           check_text(live_step_bound) == [], str(check_text(live_step_bound)))

    if failures:
        print("check-step-timeouts self-test: FAILED")
        for failure in failures:
            print(f"- {failure}")
        raise SystemExit(1)
    print("check-step-timeouts self-test: OK (unbounded steps, jobs and traps are all caught)")


def main() -> int:
    arguments = sys.argv[1:]
    if arguments == ["--self-test"]:
        self_test()
        return 0
    paths = _workflow_paths(arguments)
    if not paths:
        print("check-step-timeouts: FAILED")
        print("- no workflow files found")
        return 1
    findings = check_files(paths)
    if findings:
        print("check-step-timeouts: FAILED")
        for finding in findings:
            print(f"- {finding}")
        return 1
    print(
        f"check-step-timeouts: OK ({len(paths)} workflow file(s); every job and every step carries a deadline)"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
