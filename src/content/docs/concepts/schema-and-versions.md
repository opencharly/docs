---
title: Schema and versions
description: The CUE schema comes before the code, and every entity carries a CalVer identity.
sidebar:
  order: 5
---

> **Carve the master pattern before building the machine.** The shape of everything the factory
> accepts is carved ONCE, before any machinery is built to handle it. Nothing is copied freehand
> beside the pattern — a freehand copy drifts; a casting cannot.
>
> — [tenet 7](/vision/)

## Schema Driven Design

The shape of every `charly.yml` an author can write is defined in CUE, and everything that needs
that shape is generated from it: the Go types the code works with, the validation gate at the
project door, and the migration that modernizes old configs.

The rule is absolute in one direction: schema-shaped Go is **generated**, never hand-transcribed.
Regeneration on a clean tree is a no-op, and drift is treated as an incident rather than a chore.

The same principle produces this site. Each plugin's `schema/*.cue` is the single source that
generates its Go parameter types, answers the runtime `Describe` RPC, *and* renders the parameter
reference you can read on its page — so all three cannot disagree.

## CalVer identity

Every entity carries a `version:` in CalVer form (`YYYY.DDD.HHMM`) — the authoritative identity
for that candy, box or VM definition. It drives cross-repo resolution, and the highest layer
version determines a composing image's content-stable label.

Version resolution is per-entity and post-fetch. When repositories drift apart,
`charly box reconcile` aligns every pin of a repo onto one version.

## Tempering

> **Conched smooth, then tempered to set.** A candybox is brought to one correct, reproducible
> state and held there: its version read from its own contents, so it stays put whenever nothing
> changed; its candies nucleating around one matching set of versions instead of a half-pinned
> jumble.
>
> — [tenet 8](/vision/)

The failure this engineers out is the box that builds today and drifts tomorrow. Hence the
insistence on content-derived versions, aligned pins, and a rebuild that must reproduce the same
result rather than merely succeed once.

## Migrating an old project

One idempotent pass brings any legacy config to the current schema:

```bash
charly migrate
```

## See also

- **[The migrate command](/recipes/build/migrate/)** — the schema-version floor and the migration table.
- **[Reconcile](/recipes/build/reconcile/)** — aligning cross-repo version pins.
