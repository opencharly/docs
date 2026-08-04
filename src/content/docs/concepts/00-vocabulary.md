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

## Polymorphism: one keyword, added capabilities

This is the single most common source of confusion, so it is worth stating carefully.

You never declare *what kind* of entity you are writing. There is one keyword, `candy:`. You add
fields, and **each field adds a capability**:

| Add this | And the candy can also… |
|---|---|
| `package:` / `plan:` / `service:` | install one concern and prove it — it can be listed in any box's `candy:` list |
| `base:` or `from:` | be **built into a container image** of its own |
| a `plugin:` block | **extend `charly` itself** with a new verb, deploy kind or command |

**They accumulate. They are not a choice between three types.** *Layer*, *box* and *plugin* name
what a candy can **do**, not a category it belongs to — and a candy routinely does more than one.
Every plugin candy in the charly repository is also a layer: it installs packages and ships its own
`plan:`, *and* it registers a verb. Adding `plugin:` did not stop it being composable.

So the accurate model is not *"a candy is one of three things"*. It is:

> **A candy is a set of capabilities, and these words describe which ones it has.**

A candy with only `package:` is usefully called a layer. Add `base:` and people call it a box,
because now there is something to build. It did not change type — it gained a field. That is why
`charly box build` and `charly box list candies` can operate on the same file without contradiction.

This is also why the core stays small while the catalog grows: adding a verb to `charly` means
authoring a candy, not modifying `charly`.

## Nesting: where a deploy runs

A **different** idea, and conflating the two is the other half of the confusion. Capabilities
compose a *candy*, at authoring time. Nesting places a *deploy*, at run time.

> A candy is never inside another candy. A **deploy** can be inside another **deploy**.

There is no `nested:` field. **Nesting is position in the file** — indent one deploy under another,
and the inner one runs inside the outer one's venue:

```yaml
check-group:
    group:
        disposable: true
        check-group-vm:
            vm:
                from: eval-vm          # a disposable VM guest
            check-group-member:
                local:                 # ← nested: lands INSIDE the guest
                    from: check-group-app
```

The inner `local:` carries no `host:` field. That is the mechanism: it inherits the parent's venue
instead of naming one.

**Why the distinction earns its place.** A top-level `local:` deploy installs packages and systemd
units onto *the machine charly runs on*. The same four lines nested under a disposable `vm:` install
them into a throwaway guest. Nothing about the authoring shape changes — only its position — and
that position is the difference between editing your workstation and editing something built to be
destroyed.

**Nesting is not membership.** A deploy indented *under* another runs **inside** it. A deploy listed
as a sibling member runs **beside** it — a companion, reachable at `${HOST:<member>}`, sharing a
lifecycle but not a machine. Children go in; siblings go next to.

## The abbreviations

Charly words are defined above. These are the industry and project abbreviations the rest of the
site uses, each expanded once here so no page has to stop and explain it again.

| Short | In full | What it means here |
|---|---|---|
| **OCI** | Open Container Initiative | the standard governing container image format and metadata. A candy's `plan:` ships as an OCI **label** — a key/value pair stored in the image itself, so it travels with the artifact |
| **CUE** | *Configure, Unify, Execute* — a language, not an initialism you need to expand in speech | the schema language charly's config is defined in. One `.cue` file is the single source for both the Go types and the load-time validation, so a schema change cannot reach one without the other |
| **IR** | intermediate representation | the shared install plan every substrate compiles to. A compiler term: the neutral form in the middle, produced once from your candy list and consumed by the container, VM, cluster, host and Android backends alike. It is why `pod:` → `vm:` is a keyword change |
| **MCP** | Model Context Protocol | the open standard for exposing tools to an AI agent. `charly mcp serve` publishes the whole command tree over it |
| **ADE** | Agent Driven Evaluation | this project's name for "the spec is the test" — every candy ships a runnable `plan:`, and an agent can both author and grade it |
| **RDD** | Risk Driven Development | prove the riskiest assumption early, on a disposable bed, before building on it |
| **SDD** | Schema Driven Design | the CUE schema comes first; schema-shaped Go is generated from it, never hand-written |
| **CalVer** | calendar versioning | version numbers that are dates — `2026.216.1804` is day 216 of 2026 at 18:04. Every candy, box and release carries one |
| **RPC** | remote procedure call | calling a function in another process as if it were local. Charly's plugins and its MCP surface both work this way |
| **SDK** | software development kit | `github.com/opencharly/sdk`, the module a plugin imports to be a plugin |
| **CDP** | Chrome DevTools Protocol | how the `cdp:` check verb drives and inspects a real browser inside a running candybox |
| **VNC** | Virtual Network Computing | the remote-framebuffer protocol behind the `vnc:` verb, which lets a check assert what a desktop is actually displaying |
| **ADB** | Android Debug Bridge | the tool the `adb:` verb uses to reach an Android device or emulator |

## A note on the names

The confectionery names are not decoration; they are the schema. `candy:` is a real YAML keyword,
`candy/` and `box/` are real directories. Prose on this site therefore uses the same words the
files use, rather than a friendlier translation that would not match anything you can grep for.

## Next

- **[The box is the boundary](/concepts/01-the-box-is-the-boundary/)** — start of the 12-part tour.
