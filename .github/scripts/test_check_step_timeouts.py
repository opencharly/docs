#!/usr/bin/env python3
"""Prove that the step-deadline checker's SELF-TEST can fail — one mechanism at a time.

WHY THIS EXISTS. `.github/scripts/check_step_timeouts.py` ships a `--self-test`
mode, and that mode is the committed coverage of the rule. A self-test is only
evidence if it can FAIL: a checker whose self-test passes whatever the code
does proves nothing, and that failure mode is SILENT — the gate stays green
while the rule it claims to enforce has stopped being enforced.

So each mechanism of the checker is removed, one at a time, and this harness
asserts that the self-test then turns RED on the fixture that covers exactly
that mechanism. A mutant that still passes is a mechanism the self-test does
not cover, and the harness fails on it.

The mutation is an ASSERTED single-string replacement: the anchor must occur
EXACTLY once in the committed source, and the harness fails loudly when it does
not, so a moved anchor can never masquerade as a passing mutation.

WHAT IS PROVED. Each mutant removes ONE mechanism:

  mutA  the block-scalar marking      — a `timeout-minutes:` inside a `run:`
                                        body is TEXT, not a key
  mutB  the cross-job step bound       — a later job's deadline does not
                                        satisfy an earlier job's last step
  mutC  the jobs-mapping end bound     — a top-level `env:` is a sibling of
                                        `jobs:`, not a job
  mutE  the dead-step-bound rule       — a step bound at or above its job's is
                                        dead code, and must be reported
  mutF  the org-distributed exclusion  — a copy the org distributes is REPORTED
                                        by the default scan, not asserted

The mutant is written into a temporary tree that MIRRORS this repo's layout
(`.github/scripts/<mutant>`), because the checker derives its repository root
from its own path — a mutant written anywhere else would compute a different
root and would turn the self-test red for the WRONG reason, which would let a
broken mutation pass unnoticed.

usage: python3 .github/scripts/test_check_step_timeouts.py
       python3 .github/scripts/test_check_step_timeouts.py --emit <mutant> <path>
exit:  0 = every mutant turned the self-test red; 1 = a mutant still passed.
"""

from pathlib import Path
import subprocess
import sys
import tempfile

ROOT = Path(__file__).resolve().parent.parent.parent
SOURCE = ROOT / ".github" / "scripts" / "check_step_timeouts.py"

# (name, anchor, replacement, what the mutation removes, the self-test case
#  that must turn red).
MUTANTS = [
    (
        "mutA-nomark",
        "    skip = [False] * len(lines)",
        "    skip = [False] * len(lines)\n    return skip  # MUTANT: the block-scalar marking disabled",
        "the block-scalar marking",
        "a block scalar's body is not a deadline",
    ),
    (
        "mutB-crossjob",
        "            step_end = job_end",
        "            step_end = len(lines)  # MUTANT: the cross-job step bound removed",
        "the cross-job step bound",
        "a later job's deadline does not satisfy an earlier job's step",
    ),
    (
        "mutC-jobsend",
        "    jobs_end = len(lines)\n    for key in keys:\n        if key[0] > jobs_index and key[1] <= jobs_indent:\n            jobs_end = key[0]\n            break",
        "    jobs_end = len(lines)  # MUTANT: the jobs-mapping end bound removed",
        "the jobs-mapping end bound",
        "a top-level env: is not a job",
    ),
    (
        "mutE-deadbound",
        "            if step_minutes is not None and job_minutes is not None and step_minutes >= job_minutes:",
        "            if False:  # MUTANT: the dead-step-bound rule removed",
        "the dead-step-bound rule",
        "a step bound that is not shorter than its job's is reported",
    ),
    (
        "mutF-orgdistributed",
        "        reason = ORG_DISTRIBUTED.get(label)",
        "        reason = None  # MUTANT: the org-distributed exclusion removed",
        "the org-distributed exclusion",
        "an org-distributed copy is not asserted by the default scan",
    ),
]


def emit(name: str, destination: str) -> int:
    """Write ONE mutant to a path, so another harness can use it as a control.

    The anchor assertion is the same one the harness makes: an anchor that has
    moved must FAIL LOUDLY here too, because a mutant that is not the mutation
    it claims to be is a control that proves nothing.
    """
    text = SOURCE.read_text(encoding="utf-8")
    for candidate, anchor, replacement, what, _case in MUTANTS:
        if candidate != name:
            continue
        count = text.count(anchor)
        if count != 1:
            print(
                f"FAIL: the anchor for {what} occurs {count} times, expected 1",
                file=sys.stderr,
            )
            return 1
        target = Path(destination)
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(text.replace(anchor, replacement), encoding="utf-8")
        print(f"emitted {target} — {what} removed")
        return 0
    print(f"FAIL: no mutant named {name!r}", file=sys.stderr)
    return 1


def main() -> int:
    arguments = sys.argv[1:]
    if arguments[:1] == ["--emit"]:
        if len(arguments) != 3:
            print("usage: test_check_step_timeouts.py --emit <mutant> <path>", file=sys.stderr)
            return 2
        return emit(arguments[1], arguments[2])

    text = SOURCE.read_text(encoding="utf-8")
    failures: list[str] = []
    passed = 0

    for name, anchor, replacement, what, case in MUTANTS:
        count = text.count(anchor)
        if count != 1:
            failures.append(
                f"{name}: the anchor for {what} occurs {count} times, expected 1 — "
                f"the mutation cannot be applied, so it would prove nothing"
            )
            continue
        with tempfile.TemporaryDirectory() as temporary:
            scripts = Path(temporary) / ".github" / "scripts"
            scripts.mkdir(parents=True)
            mutant = scripts / f"{name}.py"
            mutant.write_text(text.replace(anchor, replacement), encoding="utf-8")
            completed = subprocess.run(
                [sys.executable, str(mutant), "--self-test"],
                capture_output=True,
                text=True,
            )
        output = completed.stdout + completed.stderr
        if completed.returncode == 0:
            failures.append(
                f"{name}: the self-test still PASSED with {what} removed — "
                f"the self-test does not cover that mechanism"
            )
            continue
        if case not in output:
            failures.append(
                f"{name}: the self-test failed, but not on the case that covers "
                f"{what} (expected {case!r} in the output)"
            )
            continue
        passed += 1
        print(f"ok  {name} — {what} removed, and the self-test turned red on it")

    if failures:
        print(f"test_check_step_timeouts: FAIL ({len(failures)})")
        for failure in failures:
            print(f"- {failure}")
        return 1
    print(
        f"test_check_step_timeouts: OK ({passed} mutants; every one of them turns "
        f"the self-test red)"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
