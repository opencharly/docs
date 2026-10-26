#!/usr/bin/env python3
"""Fail the build when this repo's dependency tree carries a known advisory.

WHY. The production tree of this repo was, until opencharly/docs#159, carrying
GHSA-rj75-hqrm-r3gf (PostCSS quadratic complexity in flat selector parsing)
for weeks: it was visible in `npm audit` and in nobody's build. A tree that
REPORTS a finding on every run trains its readers to ignore the report, and
the finding that mattered was in the output the whole time. opencharly/docs#163
asks for the control that ends that: the audit becomes a GATE.

WHAT IT CHECKS. The tree npm resolves from the committed lockfile -- the same
tree `npm ci` installs, read from the lockfile alone, so the check does not
depend on an install having run. BOTH trees are asserted:

  * the PRODUCTION tree -- what the site ships, and what opencharly/docs#159's
    kind of advisory lands in;
  * the DEV tree -- the deploy tool, `wrangler`, which holds the Cloudflare
    Pages token and runs privileged during a deploy. opencharly/docs#163's own
    reasoning: "the deploy path is privileged".

A finding in EITHER tree fails the check. The production tree is what the
site ships; the dev tree is a tool that holds deployment credentials and
parses responses from a remote service, and opencharly/docs#163 cleared it
with a scoped `overrides` entry rather than leaving it to be re-read.

WHAT IT DOES NOT DO. It does not decide that a finding is acceptable, and it
does not ignore a severity. The remediation for a finding is a dependency
change (a bump, or a scoped `overrides` entry), which is a change to the
lockfile -- and this check reads that lockfile, so the two cannot drift.

THE REPORT IS A REPORT, NOT A SUBSTITUTE FOR THE GATE. npm's exit code is 1
for findings and 1 for some failures too, so the DISCRIMINATOR IS THE JSON:
a run whose output does not parse as an audit report is an ERROR and fails
this check loudly. A check that cannot read the report must never read as a
pass -- that is the difference between a gate and a decoration.

NO MOCKED AUDIT. The self-test below drives the real `npm audit` against real
fixtures, against the real npm advisory database. Nothing here simulates an
advisory.
"""

from __future__ import annotations

import json
import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent.parent

# The fixture's vulnerable package, and WHY it is that one: GHSA-rj75-hqrm-r3gf
# covers `postcss-selector-parser < 7.1.6`, a PUBLISHED advisory with a FIXED
# upper bound. Pinning 6.1.4 therefore keeps the fixture in the advisory range
# for as long as the advisory exists -- it is not a fixture that drifts with a
# transitive bump, and it is not a hand-written "advisory" the checker trusts
# because the checker was told about it.
VULNERABLE_PACKAGE = "postcss-selector-parser"
VULNERABLE_VERSION = "6.1.4"
VULNERABLE_ADVISORY = "GHSA-rj75-hqrm-r3gf"

# A tree npm cannot audit is an error, never a pass.
AUDIT_TIMEOUT_SECONDS = 300


class AuditError(Exception):
    """The audit could not produce a report. Never a pass."""


def _run_audit(directory: Path, omit_dev: bool) -> dict:
    """Run `npm audit --json` and return the parsed report.

    The report is REQUIRED to carry the keys the check reads. A report that
    parses as JSON but carries no `vulnerabilities` map is not a report of
    this shape, and believing it would be believing a verdict that was never
    produced.
    """
    command = ["npm", "audit", "--json"]
    if omit_dev:
        command.insert(2, "--omit=dev")
    try:
        completed = subprocess.run(
            command,
            cwd=directory,
            capture_output=True,
            text=True,
            timeout=AUDIT_TIMEOUT_SECONDS,
        )
    except FileNotFoundError as error:
        raise AuditError(f"npm is not on PATH: {error}") from error
    except subprocess.TimeoutExpired as error:
        raise AuditError(f"npm audit did not finish within {AUDIT_TIMEOUT_SECONDS}s") from error

    try:
        report = json.loads(completed.stdout)
    except json.JSONDecodeError:
        report = None

    # ONE guard, ONE error. npm reports its own failures in the same JSON
    # channel it reports findings in -- a tree with no lockfile comes back as
    # `{"error": {"code": "ENOLOCK", ...}}` -- so a report that does not carry
    # a `vulnerabilities` map is npm saying it could not audit, whatever the
    # exit code was. That is an ERROR, and the check fails loudly: a check
    # that could not read the report must never read as a pass.
    if not isinstance(report, dict) or "vulnerabilities" not in report:
        raise AuditError(
            "npm audit did not produce an audit report "
            f"(exit {completed.returncode}): "
            f"{(completed.stderr.strip() or completed.stdout.strip())[:400]}"
        )
    vulnerabilities = report["vulnerabilities"]
    if not isinstance(vulnerabilities, dict):
        raise AuditError("npm audit produced a `vulnerabilities` map that is not an object")
    return report


def _advisories(vulnerability: dict) -> list[dict]:
    """The advisory entries of one vulnerable package.

    npm reports a package's `via` as either an ADVISORY (an object with a
    title, a severity and a URL) or the NAME of another package that carries
    one. Only the first kind is an advisory of this package.
    """
    entries = []
    for via in vulnerability.get("via", []) or []:
        if isinstance(via, dict):
            entries.append(
                {
                    "title": via.get("title", ""),
                    "url": via.get("url", ""),
                    "severity": via.get("severity", ""),
                    "range": via.get("range", ""),
                }
            )
    return entries


def _reached_through(vulnerability: dict) -> list[str]:
    """The names of the packages this one carries a finding THROUGH."""
    names = []
    for via in vulnerability.get("via", []) or []:
        if isinstance(via, str):
            names.append(via)
    return names


def check_tree(directory: Path) -> list[dict]:
    """Every finding in the tree, each labelled with the tree it sits in."""
    full = _run_audit(directory, omit_dev=False)
    production = _run_audit(directory, omit_dev=True)

    production_names = set(production["vulnerabilities"].keys())
    findings = []
    for name, vulnerability in sorted(full["vulnerabilities"].items()):
        findings.append(
            {
                "name": name,
                "severity": vulnerability.get("severity", "unknown"),
                "tree": "production" if name in production_names else "dev",
                "range": vulnerability.get("range", ""),
                "nodes": vulnerability.get("nodes", []),
                "advisories": _advisories(vulnerability),
                "through": _reached_through(vulnerability),
                "fix": vulnerability.get("fixAvailable"),
            }
        )
    return findings


def _format_findings(findings: list[dict]) -> list[str]:
    lines = []
    for finding in findings:
        lines.append(
            f"- {finding['name']} ({finding['severity']}) -- the {finding['tree']} tree"
        )
        for node in finding["nodes"]:
            lines.append(f"    at {node}")
        if finding["range"]:
            lines.append(f"    affected versions: {finding['range']}")
        for advisory in finding["advisories"]:
            lines.append(f"    {advisory['title']} ({advisory['severity']})")
            if advisory["url"]:
                lines.append(f"      {advisory['url']}")
        for through in finding["through"]:
            lines.append(f"    reached through {through}")
        fix = finding["fix"]
        if isinstance(fix, dict):
            lines.append(
                f"    npm's suggested fix: {fix.get('name')} {fix.get('version')}"
                + (" (a MAJOR move)" if fix.get("isSemVerMajor") else "")
            )
        elif isinstance(fix, bool):
            lines.append("    npm's suggested fix: a non-breaking upgrade")
    return lines


def _write_fixture(root: Path, name: str, dependencies: dict, dev_dependencies: dict) -> Path:
    """A fixture tree with a real lockfile, built by npm itself."""
    directory = root / name
    directory.mkdir(parents=True, exist_ok=True)
    manifest = {
        "name": name,
        "version": "0.0.0",
        "private": True,
    }
    if dependencies:
        manifest["dependencies"] = dependencies
    if dev_dependencies:
        manifest["devDependencies"] = dev_dependencies
    (directory / "package.json").write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
    completed = subprocess.run(
        ["npm", "install", "--package-lock-only", "--no-audit", "--no-fund"],
        cwd=directory,
        capture_output=True,
        text=True,
        timeout=AUDIT_TIMEOUT_SECONDS,
    )
    if completed.returncode != 0:
        raise AuditError(
            f"could not build the fixture lockfile for {name}: {completed.stderr.strip()[:400]}"
        )
    return directory


def self_test() -> None:
    """Prove the checker on real fixtures, against the real advisory database."""
    failures: list[str] = []

    def expect(label: str, condition: bool, detail: str = "") -> None:
        if not condition:
            failures.append(f"{label}{': ' + detail if detail else ''}")

    with tempfile.TemporaryDirectory(prefix="audit-gate-self-test-") as temporary:
        root = Path(temporary)

        # (1) A PRODUCTION finding must be caught -- this is the arm
        # opencharly/docs#163 asks for by name.
        vulnerable = _write_fixture(
            root,
            "vulnerable-production",
            {VULNERABLE_PACKAGE: VULNERABLE_VERSION},
            {},
        )
        findings = check_tree(vulnerable)
        expect(
            "a vulnerable production fixture is reported",
            len(findings) == 1,
            str([f["name"] for f in findings]),
        )
        if findings:
            expect(
                "the production finding is labelled as the production tree",
                findings[0]["tree"] == "production",
                findings[0]["tree"],
            )
            expect(
                f"the production finding names {VULNERABLE_ADVISORY}",
                any(
                    VULNERABLE_ADVISORY in advisory["url"]
                    for advisory in findings[0]["advisories"]
                ),
                str(findings[0]["advisories"]),
            )
        else:
            failures.append("the vulnerable production fixture produced no finding to label")

        # (2) A clean tree must NOT be reported -- a gate that fails on
        # everything is not a gate.
        clean = _write_fixture(root, "clean", {}, {})
        clean_findings = check_tree(clean)
        expect(
            "a clean fixture produces no finding",
            clean_findings == [],
            str([f["name"] for f in clean_findings]),
        )

        # (3) A DEV finding must be caught too: the deploy tool holds the
        # Cloudflare token, so its tree is watched as well.
        vulnerable_dev = _write_fixture(
            root,
            "vulnerable-dev",
            {},
            {VULNERABLE_PACKAGE: VULNERABLE_VERSION},
        )
        dev_findings = check_tree(vulnerable_dev)
        expect(
            "a vulnerable dev fixture is reported",
            len(dev_findings) == 1,
            str([f["name"] for f in dev_findings]),
        )
        if dev_findings:
            expect(
                "the dev finding is labelled as the dev tree",
                dev_findings[0]["tree"] == "dev",
                dev_findings[0]["tree"],
            )

        # (4) A tree npm cannot audit must FAIL, never pass silently. npm
        # reports that in the same channel it reports findings in -- a tree
        # with no lockfile comes back as `{"error": {"code": "ENOLOCK"}}` --
        # so the check must read it as an error rather than as an empty audit.
        broken = root / "no-lockfile"
        broken.mkdir(parents=True, exist_ok=True)
        (broken / "package.json").write_text(
            json.dumps({"name": "no-lockfile", "version": "0.0.0", "private": True}) + "\n",
            encoding="utf-8",
        )
        try:
            check_tree(broken)
        except AuditError:
            pass
        else:
            failures.append("an unauditable tree did not raise an error")

    if failures:
        print("check-dependency-advisories self-test: FAILED")
        for failure in failures:
            print(f"- {failure}")
        raise SystemExit(1)
    print(
        "check-dependency-advisories self-test: OK (a production finding, a dev finding and a "
        "clean tree are all told apart, and an unauditable tree is an error)"
    )


def main() -> int:
    arguments = sys.argv[1:]
    if arguments == ["--self-test"]:
        self_test()
        return 0
    directory = Path(arguments[0]).resolve() if arguments else ROOT
    if not (directory / "package-lock.json").is_file():
        print("check-dependency-advisories: FAILED")
        print(f"- no package-lock.json in {directory}: there is no tree to audit")
        return 1
    try:
        findings = check_tree(directory)
    except AuditError as error:
        print("check-dependency-advisories: FAILED")
        print(f"- the tree could not be audited: {error}")
        return 1
    if findings:
        production = [f for f in findings if f["tree"] == "production"]
        dev = [f for f in findings if f["tree"] == "dev"]
        print("check-dependency-advisories: FAILED")
        print(
            f"- {len(findings)} finding(s) in the dependency tree "
            f"({len(production)} in the production tree, {len(dev)} in the dev tree)"
        )
        for line in _format_findings(findings):
            print(line)
        return 1
    print("check-dependency-advisories: OK (no known advisory in the production tree or the dev tree)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
