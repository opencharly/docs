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
  commit lives there.
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
- The merge gate is the **org-wide** `charly/pr-validator` (required check
  `validate / validate`, defined in `opencharly/.github`); this repo carries no
  per-repo candy gate.
- The repo's generation workflow runs the full pipeline on every push to `main`
  and every PR: clone the pinned charly, build the binary, regenerate the
  generated half, FAIL on any drift, build Astro, deploy. A drift failure means a
  regeneration must land.

## Modify this repo

- Hand-authored pages (`start/`, `concepts/`, `guides/`) are edited here directly.
- Generated pages are never edited here: `index.md` projects the charly
  `README.md`; `grievances`/`vision`/`liberation` project charly's root files;
  `reference/**` projects the pinned charly checkout; `recipes/**` projects the
  marketplace corpus. Edit the source, then land a regeneration PR here that
  bumps the pinned charly commit and carries the regenerated pages.
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
