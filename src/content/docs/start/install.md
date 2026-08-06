---
title: Install
description: Get the charly CLI onto your machine — as a development checkout or as a native package.
sidebar:
  order: 1
---

**Install `charly` as a native package for your distribution.** That is the supported way to run
it, and it is what the rest of this site assumes: every other page is written for a machine with
`charly` installed and no charly checkout anywhere.

A development checkout is the other thing on this page, and it is for working ON charly — not for
using it.

## Install (native package)

Build the package from a source tree once, then install it with your own package manager. The
install step is always yours to run: no task installs anything system-wide.

```bash
task build:pkg:arch   && sudo pacman -U dist/*.pkg.tar.zst    # Arch / CachyOS / Manjaro
task build:pkg:fedora && sudo dnf install dist/*.rpm          # Fedora
task build:pkg:debian && sudo apt install ./dist/*.deb        # Debian / Ubuntu
```

Each `build:pkg:*` task drives `charly box pkg`, which builds the repository's bundled
native-package sources into a plain artifact under `dist/`. The system-wide install is an explicit,
separate command — never a side effect of building.

The Arch package's `pkgver()` derives the same CalVer `charly version` prints, so
`pacman -Q opencharly-git` and `charly version` always agree. Its dependencies cover the full
runtime surface — `podman`, `fuse-overlayfs` and `slirp4netns` for rootless containers,
`qemu-full`, `libvirt`, `edk2-ovmf` and `swtpm` for `charly vm`, and `gnupg`, `pinentry`,
`gocryptfs` and `tailscale` for secrets, encrypted volumes and tunnels.

Once installed, `charly` needs nothing else: `--repo <owner>/<repo>` reads a published project
straight from git, and `charly box new project <dir>` starts one of your own. Nothing on this site
asks you to clone this repository.

## Development checkout (working ON charly)

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
