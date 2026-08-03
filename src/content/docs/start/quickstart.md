---
title: Quickstart
description: Read a real box, build it, enter it, and prove it works — four commands, one config file.
sidebar:
  order: 2
---

Everything below acts on one file. Read it first — building something you have not seen is how
charly stops making sense three commands in.

## The file

This is [`tutorial-shell`](/reference/box/fedora/tutorial-shell/), quoted in full from
`box/fedora/box/tutorial-shell/charly.yml`. It is a real box in the repository, and a
[check bed](/concepts/09-disposability-is-the-license/) re-proves it on every acceptance run:

```yaml
tutorial-shell:
    candy:
        description: |-
            The teaching box behind opencharly.ai's quickstart — a minimal, real dev shell
            ...
        base: fedora
        candy:
            - '@github.com/opencharly/charly/candy/supervisord:v2026.201.0706'
            - '@github.com/opencharly/charly/candy/ripgrep:v2026.201.0706'
            - '@github.com/opencharly/charly/candy/sshd:v2026.201.0706'
        plan:
            - check: composition landed both the tool candy and the service candy in one image — rg and sshd are on PATH together
              id: tutorial-shell-composition
              exit_status: 0
              stdout:
                - contains: /usr/bin/rg
                - contains: sshd
              command: command -v rg && command -v sshd
```

Four things are going on, and they are the whole model:

- **`candy:`** is the only entity keyword. This node carries `base:`, which makes it a **box** — a
  buildable container image. A node without `base:` would be a layer instead.
- **`base: fedora`** points at another box defined next door, not an external registry image. A
  base can be either.
- **the `candy:` list** composes three candies: a tool (`ripgrep`), a service (`sshd`), and the
  container init that runs services (`supervisord`). Each installs one concern.
- **`plan:`** is the acceptance spec, and it is mandatory. This one asserts a cross-candy
  invariant — that the tool and the service landed in the *same* image, which neither candy can
  assert on its own.

New to the vocabulary? [The words](/concepts/00-vocabulary/) defines candy, box and candybox in
five minutes.

## Build it

```bash
charly -C box/fedora box validate              # the schema gate — silence is the pass
charly -C box/fedora box build tutorial-shell
```

`box build` resolves the candy graph, generates a multi-stage Containerfile, and builds the image.
The acceptance plan of every composed candy is baked into the result as an OCI label, so the image
can be tested later without this repository.

The `-C box/fedora` says which project directory to read. Boxes live in the `box/<distro>`
submodules, and `-C` points `charly` at one.

## Enter it

```bash
charly -C box/fedora shell tutorial-shell
```

You are now inside the **candybox** — the running, isolated form of that box. There is no command
filter: `dnf` works, `rg` works, anything you install works. It runs rootless at uid 1000 with no
`--privileged`. [Why that is the safe arrangement →](/concepts/01-the-box-is-the-boundary/)

## Prove it

```bash
charly -C box/fedora check box tutorial-shell     # run the baked plan against the image
```

```
25 steps: 20 passed, 0 failed, 5 skipped
```

The five skips are the `context: [runtime]` steps — a service cannot be running inside an image.
For those you need a deployment, which is what the bed does:

```bash
charly -C box/fedora check run tutorial-shell-dev
```

```
[image-build]         PASS after 2m5.252s
[check-image]         PASS after 15.563s
[deploy-add]          PASS after 15.979s
[start]               PASS after 9.347s
[check-live]          PASS after 15.792s
[update]              PASS after 1m0.956s
[check-live-rebuild]  PASS after 15.623s
[cleanup]             PASS after 5.542s
PASS (steps=13)
```

One command: build, deploy, bring to steady state, run the plan, then **destroy and rebuild from
scratch** and run it again, then tear everything down. That second `check-live-rebuild` is the
interesting one — it is what separates "it worked once" from "it reproduces".

This is the stage most toolchains do not have, and it is affordable only because the deploy is
declared `disposable: true`.

## Change the mold

The same candies are not tied to containers. Apply one directly to your workstation:

```bash
charly bundle add host ripgrep
charly bundle del host        # reversed precisely, from a recorded ledger
```

Swap the substrate in a deploy and the same list installs into a VM guest over SSH, or generates
Kubernetes manifests, or installs apps onto a phone. No second vocabulary.
[One recipe, many molds →](/concepts/02-one-recipe-many-molds/)

## Where to go next

- **[The words](/concepts/00-vocabulary/)** — the vocabulary, defined once.
- **[The concepts tour](/concepts/01-the-box-is-the-boundary/)** — twelve short pages, in the order
  the project's own [vision](/vision/) states them.
- **[Authoring a candy](/guides/authoring-a-candy/)** — start your own project.
- **[Recipe cards](/recipes/)** — the dedicated page for every candy, box and verb.
