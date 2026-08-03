---
title: Candies and boxes
description: A candy installs one concern; a box is composed from a list of them. One recipe, many molds.
sidebar:
  order: 1
---

> **One recipe, many boxes.** A single declarative recipe — candies stacked into a box — pours
> into every mold: an interactive shell, a managed pod, a host workstation, a k8s cluster, a
> bootable VM, an Android device.
>
> — [tenet 2](/vision/)

## A candy

A **candy** is a directory under `candy/<name>/` holding one `charly.yml`, and it installs a
single concern. It declares what it needs — packages, files, services, ports, environment — and
an ordered `plan:` of steps to get there.

```yaml
ripgrep:
  candy:
    version: 2026.144.1443
    description: |
      Fast recursive text search (rg). Installs the ripgrep package, which provides the `rg`
      binary at /usr/bin/rg.
    package:
      - ripgrep
    plan:
      - check: the rg binary is installed at /usr/bin/rg
        file:
          file: /usr/bin/rg
          exists: true
```

Three things are mandatory on every candy, and they are what make the catalog on this site
possible: a CalVer `version:`, a non-empty `description:`, and a `plan:` carrying at least one
deterministic `check:` step. `charly box validate` enforces all three.

## A box

A **box** is a container image. It is the same `candy:` kind — there is no separate `box:`
keyword — distinguished by carrying a `base:` (an external base image) or a `from:` (a builder
reference). A node with neither is a layer fragment; a node with either is an image.

```yaml
my-box:
  candy:
    version: 2026.200.1200
    description: A dev shell with search and a Python runtime.
    base: fedora
    candy:
      - ripgrep
      - python
```

Composition is transitive and topologically sorted. `require:` expresses ordering ("install this
first"); `candy:` expresses composition ("splice these in here").

## Why the distinction is thin on purpose

Because a box is just a candy that happens to name a base, the same recipe can be applied
somewhere that has no image at all — a host, a VM guest, a phone. That is what makes
[the deploy stage](/concepts/lifecycle/) possible without a second vocabulary: you are always
applying candies, and only the substrate changes.

## Browse them

- **[Candy reference](/reference/candy/ripgrep/)** — every defined candy, with its packages,
  services and acceptance plan.
- **[Box reference](/reference/box/fedora/fedora/)** — every defined box and what it composes.

Both catalogs list what is **defined**, not what happens to be enabled or built by default.
