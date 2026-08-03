---
title: Quickstart
description: Build a box, run it, deploy it, and prove it works — one command per lifecycle stage.
sidebar:
  order: 2
---

One command per stage of the lifecycle. Each of these is a real, working invocation.

## Build

```bash
charly box build fedora
```

A box is a container image composed from a candy list. `charly box build` resolves the candy
graph, generates a multi-stage Containerfile, and builds it.

```bash
# a box living in a submodule — charly resolves cross-repo refs
charly -C box/cachyos box build cachyos
```

## Run

```bash
charly shell fedora     # drop into an interactive shell
charly start jupyter    # run it as a managed pod
charly config jupyter   # configure as a systemd service (quadlet + secrets + volumes)
```

## Deploy

The same candies apply to substrates other than containers — a host, a VM, a Kubernetes cluster,
an Android device:

```bash
charly bundle add host ripgrep
charly bundle add host fedora-coder --with-services --yes
charly bundle del host      # reverses everything, via recorded ReverseOps and an install ledger
```

`charly bundle del` is not a best-effort cleanup: every applied step records how to undo itself,
so teardown replays the ledger backwards.

## Evaluate

```bash
charly check run check-pod
```

A **check bed** is a disposable deployment that exists to be destroyed. `charly check run` drives
the whole sequence — build, deploy, bring to steady state, run the baked acceptance plan, tear
down — and reports a verdict.

This is the stage most tools do not have, and it is why every candy on this site shows an
**acceptance plan**: the spec is the test, baked into the image and runnable against a live
deployment.

## Building a bootable VM

```bash
charly box build <my-bootc-box>              # a candy: with base: + bootc: true
charly vm build  <my-bootc-vm> --type qcow2  # a kind:vm with source.kind: bootc
charly vm create <my-bootc-vm>
```

## Where to go next

- **[Candies and boxes](/concepts/candies-and-boxes/)** — what you are actually composing.
- **[Candyboxing](/concepts/candyboxing/)** — why the boundary is the security model.
- **[Recipe cards](/recipes/)** — the dedicated page for every candy, box and verb.
