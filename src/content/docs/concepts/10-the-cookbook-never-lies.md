---
title: The cookbook never lies
description: Documentation speaks in the present tense, and a running system always outranks a page describing it.
sidebar:
  order: 10
---

> **The cookbook never lies.** The cookbook — every recipe card, house rule, and tasting note in
> the factory — is a living document that speaks only in the present tense: the moment a batch
> contradicts a page, the page is wrong, and it is corrected the same day, everywhere the stale
> claim appears.
>
> — [tenet 10](/vision/)

## The idea

Stale documentation is worse than none. Absent docs make you go and look; wrong docs make you
confident. And the cost compounds — every task that starts from a wrong page inherits the error,
including the tasks that then write more pages.

Three rules keep the corpus honest.

**A running system outranks a page.** When a live bed contradicts a document, the document is
wrong. Not "possibly out of date" — wrong, and corrected the same day. The reasoning is simple:
the bed just ran.

**Present tense only.** Documentation describes how things work *now*. What happened — past
changes, retired names, completed migrations — lives in a dated changelog, never on a reference
page. A page that narrates its own history is a page that will eventually describe something that
no longer exists.

**Fix the claim, not the sentence.** A false statement is rarely in one place. Correcting the one
you happened to find, and leaving three paraphrases of it elsewhere, converts a visible error into
an invisible one. The sweep is keyed to the claim, in every wording it appears in.

The structural answer to all three is the one this site is built on: **do not write down what can
be projected.** A copy drifts; a projection cannot. The reference and recipe halves of this site
are generated from the sources they describe, so the largest surface of the corpus is incapable of
going stale.

## In practice

Regenerate the generated half from the sources:

```bash
task docs:sync
```

Then prove it was already current — regeneration on a clean tree must change nothing:

```bash
task docs:drift
```

That command is the mechanism behind the tenet. If someone edits a generated page by hand, or
changes a candy's `description:` without regenerating, `docs:drift` fails. Staleness becomes a
build failure rather than a discovery someone makes months later.

The same discipline covers the examples on this site. The box quoted throughout these pages —
[`tutorial-shell`](/reference/box/fedora/tutorial-shell/) — is not illustrative YAML; it is a real
box with a real bed in the acceptance roster:

```bash
charly --repo opencharly/distro-fedora check run check-tutorial-shell
```

If the documented example ever stops building or stops composing, that bed fails. A reader is not
the failure detector.

## If you know docs-as-code

This goes one step further than "docs live in the repo and get reviewed". Review catches wrong
prose only when a reviewer happens to know better. Here the largest part of the corpus is not
reviewed for accuracy at all — it is *generated*, so accuracy is a property of the pipeline. What
remains hand-written is the narrative, where a human argument is the point and no projection is
possible.

## See also

- **[Every piece has a card](/concepts/03-every-piece-has-a-card/)** — what generation covers.
- **[The docs command](/recipes/build/docs/)** — the generator itself.
- **[Prove the risky thing first](/concepts/05-prove-the-risky-thing-first/)** — where "the bed wins" comes from.
