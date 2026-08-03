---
title: One recipe, many molds
description: A candy list composes into an image — and the same list installs onto a host, a VM, a cluster, or a phone.
sidebar:
  order: 2
---

> **One recipe, many boxes.** A single declarative recipe — candies stacked into a box — pours
> into every mold: an interactive shell, a managed pod, a host workstation, a k8s cluster, a
> bootable VM, an Android device. Write the recipe once; let `charly` set it in whatever shape
> the moment needs.
>
> — [tenet 2](/vision/)

## The idea

A **candy** installs one concern. A **box** is a candy that also carries a `base:`, plus a list of
other candies to compose. Composition is transitive and topologically sorted: `require:` expresses
ordering ("this must be installed first"), `candy:` expresses composition ("splice these in here").

The distinction between a candy and a box is deliberately thin — a box *is* a candy, just one that
names a base. That thinness is what makes the second half of the tenet possible. Because a box is
only a candy list plus a starting point, the same list can be applied somewhere that has no image
at all: a host, a VM guest, a phone. You are always applying candies; only the substrate changes.

Every substrate consumes the same intermediate representation, so adding one does not add a
vocabulary. Reversal is part of that IR rather than bolted on per substrate: a step can record the
operation that undoes it. You see this most directly on the host target, where those recorded
operations go into an install ledger and `charly bundle del host` replays it backwards instead of
making a best-effort guess at cleanup.

## In practice

The whole model in one worked example. First a **layer** — one concern, and the probes that prove
it ([`ripgrep`](/reference/candy/ripgrep/), quoted from `candy/ripgrep/charly.yml`):

```yaml
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

Then a **box** — the same `candy:` keyword, plus `base:` and a composition list. This is
[`tutorial-shell`](/reference/box/fedora/tutorial-shell/), quoted from
`box/fedora/box/tutorial-shell/charly.yml`, and it is the box the rest of this site uses:

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

Three candies, each teaching one distinct thing: `ripgrep` is a **tool** layer (packages and
probes, no service); `sshd` is a **service** layer; `supervisord` is the container **init** that
runs the service. The box's own check asserts the one thing neither candy can assert alone — that
they landed in the same image.

Build it, enter it, run it, prove it:

```bash
charly -C box/fedora box validate                    # the schema gate — nothing runs until it passes
charly -C box/fedora box build tutorial-shell        # → multi-stage Containerfile → image
charly -C box/fedora shell tutorial-shell            # → you are inside the candybox
charly -C box/fedora check run tutorial-shell-dev    # → build, deploy, probe, fresh rebuild, tear down
```

### The payoff: change the mold, keep the recipe

The deploy names a substrate. Swap it and the same candies land somewhere else entirely:

```bash
charly bundle add host ripgrep      # the SAME candy — installed on your workstation, no container
charly bundle del host              # reversed precisely, from the recorded ledger
```

| Substrate | Kind | What it means |
|---|---|---|
| your workstation | `local:` | candies applied to a host, over a shell or SSH |
| a virtual machine | `vm:` | libvirt/QEMU guests, candies applied inside over SSH |
| a cluster | `k8s:` | generated Kustomize manifests |
| a phone | `android:` | apps installed onto a device over adb |
| a container | `pod:` | the managed-pod case |

No second vocabulary. That is the whole tenet.

### The third role: a candy can extend charly itself

A candy carrying a `plugin:` block does not install software into a box — it teaches `charly` a
new verb, kind, or command. [`plugin-example`](/reference/candy/plugin-example/) is the canonical
one:

```yaml
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

Same file format, same validation, same acceptance plan as any other candy. See
[authoring a plugin](/guides/authoring-a-plugin/) for the full model.

:::tip[Yes, it comes with the kitchen sink]
The catalog does not stop at three candies. At the other end of the spectrum sit the
**kitchen-sink dev boxes** — [`fedora-coder`](/recipes/coder/fedora-coder/) and its
[`arch`](/recipes/coder/arch-coder/), [`debian`](/recipes/coder/debian-coder/) and
[`ubuntu`](/recipes/coder/ubuntu-coder/) siblings — around thirty candies each: five AI coding
CLIs, every language runtime, the DevOps tooling, nested containers, rootless VMs. Same recipe
format as the three-candy box above. A fully stocked kitchen really does ship with the sink.
:::

## If you know Dockerfiles and Ansible

A Containerfile is a script: ordered, imperative, and specific to images. A candy list is a
declaration, and the *same* declaration is what a host deploy consumes. So the thing you would
normally solve twice — a Dockerfile for the image, a role or a setup script for the workstation —
is written once here.

The closest familiar analogue for the reversibility is a package manager's transaction log, except
it covers files, services, and shell-profile edits too.

## See also

- **[The words](/concepts/00-vocabulary/)** — candy, box, candybox, and the three roles.
- **[Candy reference](/reference/candy/ripgrep/)** — every defined candy, with its acceptance plan.
- **[Box reference](/reference/box/fedora/tutorial-shell/)** — every defined box and what it composes.
- **[The spec is the test](/concepts/06-the-spec-is-the-test/)** — what those `check:` steps are.
