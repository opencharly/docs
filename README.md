# opencharly/docs

The documentation site for [OpenCharly](https://github.com/opencharly/charly) — the open
infrastructure compiler for you and your agents. Published at **[opencharly.ai](https://opencharly.ai)**.

Built with [Starlight](https://starlight.astro.build/) on Astro, deployed by Cloudflare Pages on
every push to `main`.

**This repo is standalone.** It is not a submodule of any other repository — `.gitmodules` pins
only the [marketplace](https://github.com/opencharly/marketplace) corpus, and the
[charly](https://github.com/opencharly/charly) repository is pinned by a CI-time commit in
[`deploy.yml`](.github/workflows/deploy.yml), which is the SOLE owner of generation, building and
publishing: it clones the pinned charly at CI time, builds the charly binary, regenerates the
generated half of the site with `charly docs generate`, fails if the committed content does not
match the pinned charly (the drift gate), builds the Astro site and deploys to Cloudflare Pages.

## Half of this repo is generated

The site has two halves, and they are maintained very differently.

**Hand-written** — the pages a website needs and a repository does not have:

```
src/content/docs/start/            install, quickstart
src/content/docs/concepts/         candies & boxes, candyboxing, lifecycle, RDD/ADE, schema
src/content/docs/guides/           authoring a plugin, the CLI
```

**Generated** — everything that already exists in the pinned charly checkout, projected rather
than copied, because a copy drifts and a projection cannot:

```
src/content/docs/index.md               charly's README.md (the home page)
src/content/docs/grievances.md          charly's GRIEVANCES.md, verbatim
src/content/docs/vision.md              charly's VISION.md, verbatim
src/content/docs/liberation.md          charly's LIBERATION.md, verbatim
src/content/docs/reference/cli/         one page per command word
src/content/docs/reference/candy/       every defined candy
src/content/docs/reference/box/         every defined box
src/content/docs/reference/plugin/      every plugin candy: providers, placement, CUE schema
src/content/docs/reference/providers.md  every reserved word → the plugin serving it
src/content/docs/recipes/               every skill in the standalone marketplace corpus
```

Every generated file carries a `DO-NOT-EDIT` header. **Do not edit them** — the next
regeneration overwrites the whole tree.

## Regenerating

The generated half is produced by `charly docs generate` (served by charly's
`candy/plugin-docs` runtime plugin) **from the charly commit this repo pins at CI time in
`deploy.yml`**.
The deploy workflow runs the regeneration on every main push and every PR, and **fails when the
committed content does not match the pinned charly** — regeneration on a clean tree is a no-op,
so a diff means the tree needs a regeneration landing:

1. edit the source in the [charly repo](https://github.com/opencharly/charly) (a candy's
   `description:`, a skill's prose, the README), which lands through charly's own PR flow;
2. open a PR here that **bumps the CI-time charly commit in `deploy.yml`** to the merged charly
   commit and **commits the regenerated pages** — run the generator locally against a charly
   checkout:

   ```bash
   cd charly && ../bin/charly docs generate --root . --out ../src/content/docs
   ```

   (or simply push the pin bump and let this workflow's drift gate list exactly what changed).

Hand-written pages (`start/`, `concepts/`, `guides/`) are edited directly in this repo; the
drift gate keeps proving the generated half still matches the pinned charly.

The home page is one of the generated ones — it is projected from charly's `README.md`. To
change the front page, change the README.
