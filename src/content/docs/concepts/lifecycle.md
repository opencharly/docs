---
title: Build, run, deploy, evaluate
description: Four stages, one config, one mental model — and the same candies throughout.
sidebar:
  order: 3
---

The four stages are not four tools. They are four things you can do with the same recipe.

## Build

`charly box build` resolves a box's candy graph, generates a multi-stage Containerfile, and
builds the image. Package installs are declarative (a `distro:` map resolved most-specific-first,
so Debian and Ubuntu can never race over one shared section), Python comes from `pixi.toml`, npm
from `package.json`, Rust from `Cargo.toml` — the generator detects each and emits the builder
stage.

What ends up in the image is also recorded *on* the image: capabilities, ports, services and the
acceptance plan are baked into `ai.opencharly.*` OCI labels. That is what makes the next stage
possible without the source.

## Run

`charly start` runs a box as a managed pod; `charly shell` drops you into it; `charly config`
configures it as a systemd service with quadlets, secrets and encrypted volumes.

Because the image carries its own labels, `charly bundle from-box` can deploy from a built image
alone — no `charly.yml` required at the destination.

## Deploy

The same candies apply to substrates that are not containers:

| Substrate | Kind | What it means |
|---|---|---|
| your workstation | `local:` | apply candies directly to a host, over a shell or SSH |
| a virtual machine | `vm:` | libvirt/QEMU guests from cloud images or bootc |
| a cluster | `k8s:` | generated Kustomize manifests |
| a phone | `android:` | apps installed onto a device over adb |
| a container | `pod:` | the managed-pod case |

Every one of them consumes the same shared InstallPlan intermediate representation. Adding a
substrate does not add a vocabulary.

Deploys are reversible by construction: each applied step records how to undo itself, and
`charly bundle del` replays the ledger backwards.

## Evaluate

This is the stage most tooling does not have. A **check bed** is a `disposable: true` deployment
that exists to be destroyed:

```bash
charly check run check-pod
```

That single command builds, deploys, brings the deployment to steady state, runs its baked
acceptance plan, reports a verdict, and tears everything down. Probes are declarative verbs —
files, ports, HTTP, D-Bus, Chrome DevTools, VNC, SPICE, Kubernetes, adb — each served by a
plugin.

See [Risk Driven Development and Agent Driven Evaluation](/concepts/rdd-and-ade/) for what the
stage is *for*.

## One config

All four stages read the same `charly.yml`. The binary that ties them together is also an MCP
server, so an agent reaches every verb over the same RPC that you reach from a shell.
