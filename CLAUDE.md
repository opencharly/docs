# docs/ — signpost (not the rule-set)

You are in the **opencharly/docs** submodule: the Starlight site published at opencharly.ai.

**Load these skills FIRST (R0):**

- `/charly-build:docs` — the `charly docs generate` verb that emits this site's generated half.
- `/charly-tools:docs-site` — the `docs-site` candy (the node/Astro toolchain) and the
  `check-docs` bed that builds and serves this site.
- `/charly-internals:skills` — when the change touches the skill corpus this site publishes.

**Generated trees are not editable here.** `vision.md`, `reference/**` and `recipes/**` are
emitted by `charly docs generate` and carry a `DO-NOT-EDIT` header; edit the SOURCE in the
superproject (or the plugins submodule) and re-run `task docs:sync`. Only the hand-authored
narrative — `index.mdx`, `start/`, `concepts/`, `guides/` — is edited in this repo.

**Authoritative rules live in the superproject's root `CLAUDE.md`.** R0–R10, the hard-cutover
policy, and AI attribution are defined there — this file only signposts and restates no rule.
History lives in this repo's `CHANGELOG/` (one file per CalVer version).
