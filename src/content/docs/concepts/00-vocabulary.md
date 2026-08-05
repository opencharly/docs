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
| **candy** | One entry in a `charly.yml` — the one kind you write for anything you **build**. Deploys are written with the substrate kinds below, and `candy:` is itself provided by a plugin rather than built in. | Not a deploy. Not the running thing. |
| **box** | A candy that carries `base:` or `from:`, which makes it a buildable **container image**. | Not the running thing. |
| **candybox** | A box in its **running, isolated form** — a rootless container, a VM, or a check bed. **This is the security boundary.** | Not the image. Not the config file. |
| **check bed** | A deploy marked `disposable: true` — a candybox that exists in order to be destroyed. | Not a test file. |
| **plan** | The ordered acceptance spec a candy carries, baked into the image as an OCI label — distinct from the install plan (the IR), the shared form every substrate compiles to (see the abbreviations below). | Not a build script. |
| **deploy** | A named instance of a box, running on a substrate. | |
| **bundle** | The set of deploys charly manages on this machine — `charly bundle add` puts a deploy in it. | |
| **substrate** | Where a deploy lands: `pod:` `vm:` `k8s:` `local:` `android:`. | |

### box vs candybox, concretely

```bash
charly --repo opencharly/distro-fedora box build tutorial-shell   # produces a BOX     — an image, sitting in storage
charly --repo opencharly/distro-fedora shell tutorial-shell       # produces a CANDYBOX — a running, isolated room
```

The box is an artifact. The candybox is a place. When this site says safety lives at the
boundary, it means the candybox's boundary — the kernel-enforced walls around the running thing —
not anything about the image's contents.

## One keyword, two shapes

This is the single most common source of confusion, so it is worth stating carefully — and
exactness here means saying what the schema actually enforces, not what would be tidy.

There is one entity keyword, `candy:`, and one filename, `charly.yml`. But a candy resolves to
**one of two shapes**, and `base:`/`from:` is the switch:

| The candy carries | It is | And it may also carry |
|---|---|---|
| neither `base:` nor `from:` | a **layer** — one installable concern | `package:` `service:` `plan:`, and a `plugin:` block |
| `base:` or `from:` | a **box** — a buildable container image | a `candy:` list of layers, `plan:` |

(`from:` inside a deploy or template means something different — it inherits a same-kind template
rather than marking a buildable image; the nesting excerpt below shows that other use.)

**The two shapes are mutually exclusive, and the schema enforces it.** `spec/schema/node.cue`
defines `#CandyValue: (*#Candy | #Image)` — a closed two-arm disjunction. Add `base:` to a candy
that declares `package:` and `charly box validate` rejects it: *`base: field not allowed` /
`package: field not allowed`*. A box does not install packages directly; it composes layers that
do.

**The one thing that genuinely is additive is `plugin:`.** A layer may also register providers, and
in this repository 86 candies do — every one of them carrying a `plan:`, so each is a real layer
*and* an extension of `charly` at the same time. That is the additive case, and it lives entirely
inside the layer shape.

So the accurate model is: **a candy is a layer or a box, never both — and a layer can additionally
be a plugin.** That is also why `charly box build` and `charly box list candies` can act on the
same file without contradiction: the file is a candy, and its `base:` decides which shape it is.

### What each shape looks like

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

**A plugin** — [`plugin-example`](/reference/candy/plugin-example/) is the layer shape plus a
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

### The vocabulary itself is open

Every keyword in this document is registered by a plugin candy — and the most surprising one is
`candy:` itself. `charly` is not a program with built-in support for containers, VMs and Kubernetes
that also accepts plugins. Its core is *kind-blind*: it loads plugins, routes a word to whichever
one claims it, and carries generic data between them. It does not know what `pod:` means.

Today's catalog registers **123 words across 73 plugin candies**:

| Class | How many | Examples |
|---|---|---|
| **deploy** substrates | 5 | `pod` `vm` `k8s` `local` `android` |
| **kind** — the entity keywords themselves | 14 | `candy` `distro` `group` `builder` `agent` |
| **verb** — probes a `plan:` can call | 35 | `file` `http` `cdp` `vnc` `adb` `kube` |
| **command** — `charly` subcommands | 45 | `bundle` `check` `candy` `clean` |
| **step** — install operations | 12 | `file` `service-custom` `reboot` |
| **builder** — multi-stage build patterns | 4 | `pixi` `npm` `cargo` `aur` |
| the build/load internals | 8 | `build:box` `loader:loader` `refs:refs` `terminal:tmux` |

A further **14 words across 13 `plugin-example-*` candies** are test fixtures — they exist to
exercise the plugin mechanisms themselves, and are excluded from the table. That exclusion is the
difference between a deploy row reading 5 and reading 7: `exampledeploy` and `examplelifecycle`
are not substrates you can put anything on. **73 real + 13 fixtures = the 86 plugin candies
counted elsewhere on this page** — the two numbers are the same set, split rather than in tension.

Read the **kind** row again: **`candy:` itself is a plugin-provided kind**, registered by
`candy/plugin-candy-kind`. The keyword this whole page is about is not privileged — it is a word
some candy claimed. [The provider index](/reference/providers/) lists every one and its owner.

So there is no fixed list of substrates, no fixed list of check verbs, and no built-in set to
petition for additions to. A plugin lives either compiled into the binary or loaded from a project's
own `candy/` directory — including a project that is not charly's, referenced by git URL. **You
extend `charly` by writing candies, as many as you like**, and a substrate you invent is the same
kind of thing as `pod:`.

That is why the core stays small while the catalog grows, and why there is no second vocabulary:
extending the tool and using the tool are the same activity.

## Nesting: where a deploy runs

A **different** idea, and conflating the two is the other half of the confusion. Capabilities
compose a *candy*, at authoring time. Nesting places a *deploy*, at run time.

> A candy is never inside another candy. A **deploy** can be inside another **deploy**.

There is no `nested:` field. **Nesting is position in the file** — indent one deploy under another,
and the inner one runs inside the outer one's venue (the host, a VM guest, or a container —
wherever the outer deploy runs):

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
