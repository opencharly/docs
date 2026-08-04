---
title: The words
description: candy, box, candybox, bed, plan — what each one means, and the one pair people conflate.
sidebar:
  order: 0
---

OpenCharly has a small private vocabulary. It is worth five minutes up front, because one pair —
**box** and **candybox** — sound like synonyms and are not, and almost every confusion downstream
starts there.

Each term below is defined once, here. Every other page on this site links back rather than
redefining.

## The terms

| Term | What it is | What it is *not* |
|---|---|---|
| **candy** | One entry in a `charly.yml`. The **only** entity kind there is — everything you author is a candy. | Not "a layer". Not "a package". |
| **box** | A candy that carries `base:` or `from:`, which makes it a buildable **container image**. | Not the running thing. |
| **candybox** | A box in its **running, isolated form** — a rootless container, a VM, or a check bed. **This is the security boundary.** | Not the image. Not the config file. |
| **check bed** | A deploy marked `disposable: true` — a candybox that exists in order to be destroyed. | Not a test file. |
| **plan** | The ordered acceptance spec a candy carries, baked into the image as an OCI label. | Not a build script. |
| **deploy** | A named instance of a box, running on a substrate. | |
| **substrate** | Where a deploy lands: `pod:` `vm:` `k8s:` `local:` `android:`. | |

### box vs candybox, concretely

```bash
charly --repo opencharly/distro-fedora box build tutorial-shell   # produces a BOX     — an image, sitting in storage
charly --repo opencharly/distro-fedora shell tutorial-shell       # produces a CANDYBOX — a running, isolated room
```

The box is an artifact. The candybox is a place. When this site says safety lives at the
boundary, it means the candybox's boundary — the kernel-enforced walls around the running thing —
not anything about the image's contents.

## One candy, three roles

There is one `candy:` keyword. What you put *inside* it decides what it is:

| What the candy declares | What it is | How it is used |
|---|---|---|
| `package:` / `plan:` / `service:` | a **layer** — one concern | spliced into any box's `candy:` list |
| …plus `base:` or `from:` | a **box** — a buildable image | `charly box build <name>` |
| …plus a `plugin:` block | a **plugin** — extends `charly` itself with a new verb, kind or command | loaded on demand, or compiled into the binary |

All three are real and shipped, and you can read each one on this site:

**A layer** — [`ripgrep`](/reference/candy/ripgrep/) installs one concern and proves it:

```yaml
# candy/ripgrep/charly.yml
ripgrep:
    candy:
        version: 2026.144.1443
        description: |
            Fast recursive text search (rg)
            ...
        package:
            - ripgrep
        plan:
            - check: the rg binary is installed at /usr/bin/rg
              file:
                file: /usr/bin/rg
                exists: true
```

**A box** — [`tutorial-shell`](/reference/box/fedora/tutorial-shell/) is the same keyword plus a
`base:`, and a list of candies to compose:

```yaml
# box/fedora/box/tutorial-shell/charly.yml
tutorial-shell:
    candy:
        description: |-
            The teaching box behind opencharly.ai's quickstart — a minimal, real dev shell
            ...
        base: fedora
        candy:
            - '@github.com/opencharly/charly/candy/ripgrep:v2026.201.0706'
            - '@github.com/opencharly/charly/candy/sshd:v2026.201.0706'
```

**A plugin** — [`plugin-example`](/reference/candy/plugin-example/) is the same keyword plus a
`plugin:` block, and it teaches `charly` a new check verb:

```yaml
# candy/plugin-example/charly.yml
plugin-example:
    candy:
        version: 2026.176.1400
        description: |-
            Reference plugin candy for the `exampleprobe` check verb ...
        plugin:
            source: github.com/opencharly/charly/candy/plugin-example
            providers:
                - verb:exampleprobe
```

One recipe-card format describes an ingredient, a finished dish, and a new piece of kitchen
equipment. That is why there is no second vocabulary to learn — and why the core can stay tiny
while the catalog grows.

## A note on the names

The confectionery names are not decoration; they are the schema. `candy:` is a real YAML keyword,
`candy/` and `box/` are real directories. Prose on this site therefore uses the same words the
files use, rather than a friendlier translation that would not match anything you can grep for.

## Next

- **[The box is the boundary](/concepts/01-the-box-is-the-boundary/)** — start of the 12-part tour.
