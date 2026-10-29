# AGENTS.md — opencharly/docs

The standalone documentation site for OpenCharly, published at **opencharly.ai**.
Starlight on Astro, deployed by Cloudflare Pages; the repo's generation workflow
is the SOLE owner of generation, build and publish. The repo pins the
[opencharly/charly](https://github.com/opencharly/charly) source by a CI-time
commit and the
[opencharly/marketplace](https://github.com/opencharly/marketplace) corpus as a
submodule.

Canonical files:

- the repo's generation workflow (`.github/workflows/`) — the SOLE owner of
  generation, the drift gate and the Cloudflare Pages deploy; the pinned charly
  and umbrella commits live there, in its own `env:` block.
- `astro.config.mjs` — the Starlight config; its sidebar `link:` targets are
  resolved against the emitted routes by generation (a dead one fails the run).
- `package.json` — the Astro/Starlight toolchain and the `astro build` script.
- `src/content/docs/start/`, `concepts/`, `guides/` — hand-authored pages.
- `src/content/docs/{index,grievances,vision,liberation}.md`, `reference/**`,
  `recipes/**` — GENERATED pages (each carries a `DO-NOT-EDIT` header).
- `README.md` — user overview only; never agent guidance.

## Load these skills first (R0)

- `/charly-build:docs` — the `charly docs generate` verb that emits this site's
  generated half.
- `/charly-tools:docs-site` — the `docs-site` candy (the Astro toolchain) and the
  `check-docs` bed that builds and serves this site.
- `/charly-internals:skills` — when the change touches the skill corpus this site
  publishes.

## Build / validate / test

- `npm ci && npm run build` — the local Astro build.
- `python3 .github/scripts/check_dependency_advisories.py` — the
  dependency-advisory gate. It audits the tree the committed lockfile resolves
  (the same tree `npm ci` installs) and FAILS on a known advisory in the
  **production** tree or the **dev** tree. The generation workflow runs it, its
  self-test, and the mutation harness that proves the self-test can fail.
- The merge gate is the **org-wide** `charly/pr-validator` (required check
  `validate / validate`, defined in `opencharly/.github`); this repo carries no
  per-repo candy gate.
- The repo's generation workflow runs the full pipeline on every push to `main`
  and every PR: clone the pinned charly, build the binary, regenerate the
  generated half, FAIL on any drift, build Astro, deploy. A drift failure means a
  regeneration must land.
- The workflow also **REPORTS each pinned input's currency** — whether the
  pinned `marketplace` commit, the pinned `charly` commit and the pinned
  umbrella commit are behind their producers' merged mains. It is reported,
  never failed: a pin that is behind is an advance available now, and the
  remedy is a regeneration PR that bumps the pin, not a gate. The drift gate
  cannot see this on its own — the PINNED sources regenerate their own (old)
  pages perfectly, so a stale pin is invisible to it. The two CI-time commits
  are recorded once, in the workflow's own `env:` block, which both the clone
  step and the report read (`.github/scripts/check_pin_currency.sh`); the
  report's own fixtures are `.github/scripts/test_check_pin_currency.sh`.

## Modify this repo

- Hand-authored pages (`start/`, `concepts/`, `guides/`) are edited here directly.
- Generated pages are never edited here: `index.md` projects the charly
  `README.md`; `grievances`/`vision`/`liberation`/`soul` project the umbrella's
  root files; `reference/**` projects the pinned charly checkout; `recipes/**`
  projects the marketplace corpus. Edit the source, then land a regeneration PR
  here that bumps the pinned charly commit — the pinned umbrella commit, for a
  narrative change, and the pinned `marketplace` commit, for a corpus change —
  and carries the regenerated pages.
- The home page is one of the generated ones — to change the front page, change
  the charly `README.md`.

## Landing

- PR-only. Every change lands through a pull request; the org-required
  `charly/pr-validator` validates the diff and body and arms native auto-merge on
  PASS. Direct pushes to `main` are blocked.
- History lives in `CHANGELOG/` (written by `tag-on-merge` at merge time); the PR
  body IS the changelog.
- The authoritative rulebook is the umbrella `AGENTS.md` in
  `opencharly/opencharly` and `charly/AGENTS.md` in the charly repo. Do not
  restate its rules here.
