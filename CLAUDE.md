# docs/ — signpost (not the rule-set)

You are in the **opencharly/docs** submodule: the Starlight site published at opencharly.ai.

**Load these skills FIRST (R0):**

- `/charly-build:docs` — the `charly docs generate` verb that emits this site's generated half.
- `/charly-tools:docs-site` — the `docs-site` candy (the node/Astro toolchain) and the
  `check-docs` bed that builds and serves this site.
- `/charly-internals:skills` — when the change touches the skill corpus this site publishes.

**Generated pages are not editable here.** `index.md`, `vision.md`, `grievances.md`,
`reference/**` and `recipes/**` are emitted by `charly docs generate` and carry a `DO-NOT-EDIT`
header; edit the SOURCE in the superproject (or the plugins submodule) and re-run `task docs:sync`.
Only `start/`, `concepts/` and `guides/` are edited in this repo.

**The home page is one of the generated ones** — it is projected from the superproject's
`README.md`. It was hand-authored until two thirds of it turned out to be README prose maintained
twice across this submodule boundary, which had already drifted. To change the front page, change
the README.

**The Astro config is checked too.** A `link:` in `astro.config.mjs`'s sidebar is resolved against
the emitted routes by `charly docs generate`; a dead one fails the run rather than rendering on
every page of the site.

**Authoritative rules live in the superproject's root `CLAUDE.md`.** R0–R10, the hard-cutover
policy, and AI attribution are defined there — this file only signposts and restates no rule.
History lives in this repo's `CHANGELOG/` (one file per CalVer version).
