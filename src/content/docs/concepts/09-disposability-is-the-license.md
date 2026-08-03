---
title: Disposability is the license
description: A box whose destruction costs nothing can be handed over completely — which is what makes autonomous iteration safe.
sidebar:
  order: 9
---

> **Every spoiled batch is a new lesson waiting to be learned.** Every candybox is both a testbed
> and the recipe for the final product by explicit design, so a failed batch costs nothing but the
> lesson inside it. A failure is feedback to be mined, never an incident to be prevented at all
> costs — and that is exactly what lets autonomous iteration be *fearless* and *safe* at once.
>
> — [tenet 9](/vision/)

## The idea

[Tenet 1](/concepts/01-the-box-is-the-boundary/) says hand over the whole toolset and trust the
walls. That is only tolerable if being wrong is cheap. Disposability is what makes it cheap: a
candybox whose destruction costs nothing can be handed over completely, because the worst outcome
is a rebuild.

So disposability is a **first-class, explicitly declared property**, and the declaration is
load-bearing:

```yaml
tutorial-shell-dev:
    pod:
        image: tutorial-shell
        disposable: true
```

`disposable: true` is the one and only authorization for autonomous destroy-and-rebuild. It is
never inferred — not from a name, not from a hostname, not from a lifecycle tag. That refusal to
infer is the entire safety property, and it comes from the obvious failure mode: inference is
exactly how an "obviously throwaway" machine turns out to have been someone's staging environment.

Note where the flag lives. It is a property of the **deploy**, not of the image. The same box can
back a disposable bed and a production deployment; only the deploy that opted in may be destroyed.

The second half of the tenet is about what you do with a failure. A spoiled batch is not an
incident to be prevented at all costs — it is feedback, and the cheapest possible feedback, since
the artifact was throwaway by construction. That is what makes autonomous iteration reasonable
rather than reckless: an agent that can destroy and rebuild freely, but only where a human wrote
`disposable: true`.

## In practice

On a disposable deploy, the destroy-and-rebuild cycle runs unattended:

```bash
charly update tutorial-shell-dev     # destroy → rebuild → recreate → start
```

Run the same command against a deploy without the flag and charly will not do it unprompted. There
is no override that infers intent from context — the authorization is the declaration.

This is also what makes the acceptance gate affordable. Every bed run ends by destroying what it
built:

```bash
charly -C box/fedora check run tutorial-shell-dev
```

```
[update]              PASS after 1m0.956s
[check-live-rebuild]  PASS after 15.623s
[cleanup]             PASS after 5.542s
PASS (steps=13)
```

Five minutes, and nothing survives it. A verification you can run that freely is one you actually
run.

## If you know cattle-not-pets

Same instinct, with the sharp edge filed off. The usual version is a convention — a naming scheme,
a tag, a shared understanding about which hosts are safe to reap — and conventions are exactly
what a tired human or an over-eager agent misreads at 2am.

Here it is a declaration in the config, checked by the tool, with no inference path around it.
"Which of these can I destroy?" has a mechanical answer.

## See also

- **[The box is the boundary](/concepts/01-the-box-is-the-boundary/)** — what disposability licenses.
- **[Disposable-flag semantics](/recipes/internals/disposable/)** — the authorization rules in full.
- **[Rebuild beats patch](/concepts/11-rebuild-beats-patch/)** — the design consequence.
