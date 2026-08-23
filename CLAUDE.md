# docs — signpost (not the rule-set)

You are in the **opencharly/docs** repository: the standalone Starlight site published at
opencharly.ai. This repo pins the [charly](https://github.com/opencharly/charly) repository as a
submodule and its `deploy.yml` workflow is the SOLE owner of generation, building and publishing.

**Load these skills FIRST (R0):**

- `/charly-build:docs` — the `charly docs generate` verb that emits this site's generated half.
- `/charly-tools:docs-site` — the `docs-site` candy (the node/Astro toolchain) and the
  `check-docs` bed that builds and serves this site.
- `/charly-internals:skills` — when the change touches the skill corpus this site publishes.

**Generated pages are not editable here.** `index.md`, `vision.md`, `grievances.md`,
`liberation.md`, `reference/**` and `recipes/**` are emitted by `charly docs generate` and carry a
`DO-NOT-EDIT` header; edit the SOURCE in the charly repository (or its plugins submodule) — the
regeneration is a PR here that bumps the `charly` submodule pin in `.gitmodules` and commits the
regenerated pages, and this repo's deploy workflow enforces it (its drift gate fails when the
committed content does not match the pinned charly).
Only `start/`, `concepts/` and `guides/` are edited directly in this repo.

**The home page is one of the generated ones** — it is projected from the pinned charly's
`README.md`. To change the front page, change the README.

**The Astro config is checked too.** A `link:` in `astro.config.mjs`'s sidebar is resolved against
the emitted routes by `charly docs generate`; a dead one fails the run rather than rendering on
every page of the site.

**Authoritative rules live in the charly repo's root `CLAUDE.md`.** R0–R10, the hard-cutover
policy, and AI attribution are defined there — this file only signposts and restates no rule.
History lives in this repo's `CHANGELOG/` (one file per CalVer version).
