---
title: Candyboxing
description: Safety lives at the boundary of the box — never in a shrunken toolset.
sidebar:
  order: 2
---

> **Secure the room, not the candy.** Safety lives at the boundary of a candybox — rootless
> containers, isolated VMs, encrypted volumes — never in a shrunken toolset. A walled room you
> can hand over *completely* beats an empty sandbox you keep narrowing.
>
> — [tenet 1](/vision/)

## The bet

The common approach to giving an agent a working environment is subtractive: fewer commands, no
network, no installs. Safety is bought by removing capability, and most of the usefulness leaves
with it.

Candyboxing inverts that. The boundary is a **disposable container, VM, or check bed** with
kernel-enforced isolation. Inside it, people and agents get the entire toolset — a full package
manager, a compiler, nested containers, a browser, root.

The practical rule that follows: **never secure by whitelisting commands.** Trust the walls, not
the tools. A whitelist is a guess about which capabilities are dangerous; a wall does not need to
guess.

## Disposability is what makes it usable

A box whose destruction costs nothing can be handed over completely, because being wrong is
cheap. That is why disposability is a first-class, explicitly-declared property:

```yaml
my-bed:
  pod:
    disposable: true
```

`disposable: true` is the one and only authorization for autonomous destroy-and-rebuild. It is
never inferred from a name, a hostname, or a lifecycle tag — inference is exactly how an
"obviously throwaway" machine turns out to have been someone's staging environment.

> **Every spoiled batch is a new lesson waiting to be learned.** A failed batch costs nothing but
> the lesson inside it. Disposability is the license to be bold.
>
> — [tenet 9](/vision/)

## Nesting

One of the molds a recipe can pour into is the factory itself: the whole `charly` line, running
inside one of its own disposable boxes. From inside that outer box it builds, deploys and tests
fresh boxes, and melts the failures back down.

That nesting is what lets verification become self-hosting — a box that builds boxes.

## See also

- **[Disposable-flag semantics](/recipes/internals/disposable/)** — the full authorization rules.
- **[Check beds](/concepts/rdd-and-ade/)** — what disposability buys you.
