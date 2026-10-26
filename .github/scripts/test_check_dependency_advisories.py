#!/usr/bin/env python3
"""Prove that the dependency-advisory checker's SELF-TEST can fail — one mechanism at a time.

WHY THIS EXISTS. `.github/scripts/check_dependency_advisories.py` ships a
`--self-test` mode, and that mode is the committed coverage of the rule: it is
what proves the gate can fail on a production-tree finding, which is the
obligation opencharly/docs#163 asks for. A self-test is only evidence if it can
FAIL — a checker whose self-test passes whatever the code does proves nothing,
and that failure mode is SILENT: the gate stays green while the rule it claims
to enforce has stopped being enforced.

So each mechanism of the checker is removed, one at a time, and this harness
asserts that the self-test then turns RED on the fixture that covers exactly
that mechanism. A mutant that still passes is a mechanism the self-test does
not cover, and the harness fails on it.

The mutation is an ASSERTED single-string replacement: the anchor must occur
EXACTLY once in the committed source, and the harness fails loudly when it does
not, so a moved anchor can never masquerade as a passing mutation.

WHAT IS PROVED. Each mutant removes ONE mechanism:

  mutA  the production audit        — the second npm audit that tells the
                                      production tree from the dev tree
  mutB  the findings loop           — the read of npm's report at all
  mutC  the tree label              — which tree a finding is reported in
  mutD  the error path              — a tree npm cannot audit is an ERROR,
                                      never a silent pass
  mutE  the advisory extraction     — the advisory titles and URLs a finding
                                      is reported with

The mutant is written into a temporary tree that MIRRORS this repo's layout
(`.github/scripts/<mutant>`), because the checker derives its repository root
from its own path.

THE `--emit` MODE IS THE WRITER, NOT A SECOND IMPLEMENTATION. Every mutant
this harness tests is written THROUGH `--emit` -- the same mode a diagnostic
caller uses -- so the mode is covered by construction rather than by a
parallel copy of the mutation, and the anchor assertion lives in exactly one
place (`emit`). A harness that mutated the source itself while shipping an
unexercised `--emit` beside it would carry the same rule twice and prove
neither copy.

usage: python3 .github/scripts/test_check_dependency_advisories.py
       python3 .github/scripts/test_check_dependency_advisories.py --emit <mutant> <path>
exit:  0 = every mutant turned the self-test red; 1 = a mutant still passed.
"""

from pathlib import Path
import subprocess
import sys
import tempfile

ROOT = Path(__file__).resolve().parent.parent.parent
SOURCE = ROOT / ".github" / "scripts" / "check_dependency_advisories.py"

# (name, anchor, replacement, what the mutation removes, the self-test case
#  that must turn red).
MUTANTS = [
    (
        "mutA-noproductionaudit",
        "    production = _run_audit(directory, omit_dev=True)",
        "    production = {\"vulnerabilities\": {}}  # MUTANT: the production audit removed",
        "the production audit",
        "the production finding is labelled as the production tree",
    ),
    (
        "mutB-nofindings",
        '    for name, vulnerability in sorted(full["vulnerabilities"].items()):',
        '    for name, vulnerability in sorted({}.items()):  # MUTANT: the findings loop removed',
        "the findings loop",
        "a vulnerable production fixture is reported",
    ),
    (
        "mutC-invertedlabel",
        '                "tree": "production" if name in production_names else "dev",',
        '                "tree": "dev" if name in production_names else "production",  # MUTANT: the tree label inverted',
        "the tree label",
        "the production finding is labelled as the production tree",
    ),
    (
        "mutD-swallowederror",
        '    if not isinstance(report, dict) or "vulnerabilities" not in report:\n'
        '        raise AuditError(\n'
        '            "npm audit did not produce an audit report "\n'
        '            f"(exit {completed.returncode}): "\n'
        '            f"{(completed.stderr.strip() or completed.stdout.strip())[:400]}"\n'
        '        )',
        '    if not isinstance(report, dict) or "vulnerabilities" not in report:\n'
        '        return {"vulnerabilities": {}}  # MUTANT: the report guard swallowed',
        "the report guard",
        "an unauditable tree did not raise an error",
    ),
    (
        "mutE-noadvisories",
        "        if isinstance(via, dict):",
        "        if False:  # MUTANT: the advisory extraction removed",
        "the advisory extraction",
        "the production finding names GHSA-rj75-hqrm-r3gf",
    ),
]


def emit(name: str, destination: str) -> int:
    """Write ONE mutant to a path, so another harness can use it as a control.

    This is the ONLY place the anchor is asserted and the ONLY place the
    mutation is applied. An anchor that has moved must FAIL LOUDLY here,
    because a mutant that is not the mutation it claims to be is a control that
    proves nothing.
    """
    text = SOURCE.read_text(encoding="utf-8")
    for candidate, anchor, replacement, what, _case in MUTANTS:
        if candidate != name:
            continue
        count = text.count(anchor)
        if count != 1:
            print(
                f"FAIL: the anchor for {what} occurs {count} times, expected 1 — "
                f"the mutation cannot be applied, so it would prove nothing",
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
            print("usage: test_check_dependency_advisories.py --emit <mutant> <path>", file=sys.stderr)
            return 2
        return emit(arguments[1], arguments[2])

    failures: list[str] = []
    passed = 0

    for name, _anchor, _replacement, what, case in MUTANTS:
        with tempfile.TemporaryDirectory() as temporary:
            scripts = Path(temporary) / ".github" / "scripts"
            scripts.mkdir(parents=True)
            mutant = scripts / f"{name}.py"
            # The mutant is written THROUGH this harness's own `--emit` mode --
            # the same path a diagnostic caller uses -- so the mode is covered
            # by construction, and the anchor assertion happens exactly once.
            written = subprocess.run(
                [sys.executable, str(Path(__file__).resolve()), "--emit", name, str(mutant)],
                capture_output=True,
                text=True,
            )
            if written.returncode != 0:
                failures.append(
                    f"{name}: the mutation could not be applied — "
                    f"{(written.stderr.strip() or written.stdout.strip())}"
                )
                continue
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
        print(f"test_check_dependency_advisories: FAIL ({len(failures)})")
        for failure in failures:
            print(f"- {failure}")
        return 1
    print(
        f"test_check_dependency_advisories: OK ({passed} mutants; every one of them turns "
        f"the self-test red)"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
