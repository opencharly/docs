---
title: Install
description: Get the charly CLI onto your machine — as a development checkout or as a native package.
sidebar:
  order: 1
---

There are two ways to run `charly`, and they are deliberately kept apart: a **development
checkout**, where the binary belongs to that checkout and nothing is installed system-wide, and a
**native package**, for using `charly` as a tool on your host.

## Development checkout

Requires Go 1.26+ and [go-task](https://taskfile.dev).

```bash
git clone --recurse-submodules https://github.com/opencharly/charly.git
cd charly
task build:binary        # builds ./bin/charly (CalVer-stamped) — never installs to the host
./bin/charly box build   # build everything
```

Every invocation against this checkout uses `./bin/charly`. There is no system-wide dev install,
and that is the point: work from several checkouts or worktrees and each gets its own
`task build:binary` and its own `./bin/charly`, with nothing shared between them.

:::caution[Use the binary you just built]
A stale `bin/charly` is the classic way to waste an afternoon — it can fail in confusing ways
that look like real bugs. If anything behaves strangely, re-run `task build:binary` and check
`charly version` against your checkout before investigating further.
:::

To start your own project, create a `charly.yml` and a `candy/` directory in any directory.
Projects predating the current schema convert in one shot with `charly migrate`, a single
idempotent pass to the latest CalVer schema.

## Native packages

For end users who want `charly` on the host system:

```bash
task build:pkg:arch   && sudo pacman -U dist/*.pkg.tar.zst    # Arch / CachyOS / Manjaro
task build:pkg:fedora && sudo dnf install dist/*.rpm          # Fedora
task build:pkg:debian && sudo apt install ./dist/*.deb        # Debian / Ubuntu
```

Each `pkg:*` task drives `charly box pkg`, which builds the repository's bundled native-package
sources into a plain artifact under `dist/`. The system-wide install step is always an explicit,
separate command — never a side effect of building.

The Arch package's `pkgver()` derives the same CalVer `charly version` prints, so
`pacman -Q opencharly-git` and `charly version` always agree. Its dependencies cover the full
runtime surface — `podman`, `fuse-overlayfs` and `slirp4netns` for rootless containers,
`qemu-full`, `libvirt`, `edk2-ovmf` and `swtpm` for `charly vm`, and `gnupg`, `pinentry`,
`gocryptfs` and `tailscale` for secrets, encrypted volumes and tunnels.

## A personal binary on your `$PATH`

```bash
task build:install-portable   # copies ./bin/charly to $HOME/.local/bin/charly
```

This writes to `$HOME`. If `$HOME/.local/bin` precedes a native-package install location in your
`$PATH`, it **shadows** the system `charly` for your user. That is fine on a single-developer
machine. On a shared host it silently changes which binary a bare `$PATH` lookup resolves to —
for another session, a script, or a deploy step — so prefer a native package there.

## Next

[Build your first box →](/start/quickstart/)
