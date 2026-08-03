# opencharly/docs

The documentation site for [OpenCharly](https://github.com/opencharly/charly) — the candy
factory for you and your agents. Published at **[opencharly.ai](https://opencharly.ai)**.

Built with [Starlight](https://starlight.astro.build/) on Astro, deployed by Cloudflare Pages on
every push to `main`.

## Half of this repo is generated

The site has two halves, and they are maintained very differently.

**Hand-written** — the pages a website needs and a repository does not have:

```
src/content/docs/index.mdx         the home page
src/content/docs/start/            install, quickstart
src/content/docs/concepts/         candies & boxes, candyboxing, lifecycle, RDD/ADE, schema
src/content/docs/guides/           authoring a plugin, the CLI
```

**Generated** — everything that already exists in the source repository, projected rather than
copied, because a copy drifts and a projection cannot:

```
src/content/docs/vision.md               VISION.md, verbatim
src/content/docs/reference/cli/          one page per command word
src/content/docs/reference/candy/        every defined candy
src/content/docs/reference/box/          every defined box
src/content/docs/reference/plugin/       every plugin candy: providers, placement, CUE schema
src/content/docs/reference/providers.md  every reserved word → the plugin serving it
src/content/docs/recipes/                every skill in the plugins corpus
```

Every generated file carries a `DO-NOT-EDIT` header. **Do not edit them** — the next
regeneration overwrites the whole tree.

## Regenerating

From a checkout of the [charly superproject](https://github.com/opencharly/charly), where this
repo is the `docs/` submodule:

```bash
task docs:sync     # regenerate into docs/
task docs:dev      # local preview at http://localhost:4321
```

`task docs:sync` runs `charly docs generate`, served by the `candy/plugin-docs` runtime plugin.
Regeneration on a clean tree is a no-op: if `git status` is dirty afterwards, a source changed.

## Local development

```bash
npm install
npm run dev      # http://localhost:4321
npm run build    # production build into dist/
npm run preview  # serve the production build
```

Node 22 (see `.node-version`).

## License

MIT — see [LICENSE](LICENSE).
