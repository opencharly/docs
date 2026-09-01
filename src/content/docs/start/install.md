---
title: Install
description: Install the charly CLI — from source, or with the mise dev-tool manager — and put it on your $PATH.
sidebar:
  order: 1
---

**Install `charly` once, then use it from anywhere.** The rest of this site is written for a
machine with `charly` installed and no charly checkout anywhere: `--repo <owner>/<repo>` reads a
published project straight from git, and `charly box new project <dir>` starts one of your own.
Nothing on any other page asks you to clone this repository.

Two install paths: the **published release binary** via [mise](https://mise.jdx.dev) (no toolchain needed), or a **source build** with Go + go-task. Working ON charly is the section after both.

## Install

Requires Go 1.26+ and [go-task](https://taskfile.dev).

```bash
git clone --recurse-submodules https://github.com/opencharly/charly.git
cd charly
task build:binary              # builds ./bin/charly (CalVer-stamped) — never installs to the host
task build:install-portable    # copies it to $HOME/.local/bin/charly
```

The install step is always yours to run: `build:binary` never installs anything, and
`install-portable` writes only into your own `$HOME`. Nothing here touches a system directory or
needs `sudo`.

Because it writes to `$HOME/.local/bin`, it **shadows** any other `charly` earlier on your `$PATH`
for your user. That is fine on a single-developer machine; on a shared host it silently changes
which binary a bare `$PATH` lookup resolves to — for another session, a script, or a deploy step.

`charly version` prints the CalVer the binary was stamped with, so you can always tell which build
is on your `$PATH`.

Its runtime dependencies are the ones the features you use need — `podman`, `fuse-overlayfs` and
`slirp4netns` for rootless containers, `qemu-full`, `libvirt`, `edk2-ovmf` and `swtpm` for
`charly vm`, and `gnupg`, `pinentry`, `gocryptfs` and `tailscale` for secrets, encrypted volumes and
tunnels. Install the ones you need with your own package manager; `charly doctor` reports what is
missing.

## Install with mise

[mise](https://mise.jdx.dev) is a polyglot dev-tool version manager (asdf-compatible, Rust). It
installs the **published release binary** straight from GitHub Releases — no Go toolchain, no
source build:

```bash
mise use github:opencharly/charly                    # latest release
mise use github:opencharly/charly@2026.234.1727      # pin a CalVer
```

`mise use` writes the tool into your project's `mise.toml` and installs it. The `charly` shim
lands on your `$PATH`; without activation, `mise x` runs it:

```bash
charly version            # via the mise shim
mise x -- charly version  # without the shim on PATH
```

The binary is the same CalVer-stamped release build the package repos ship — `charly version`
tells you which one. Runtime dependencies are the ones the features you use need; `charly doctor`
reports what is missing.

:::note[Why `github:opencharly/charly`?]
mise's GitHub backend (`github:org/repo`) installs release assets from GitHub Releases — the
modern replacement for the deprecated `ubi:` backend. The full backend spec is what resolves; a
bare `charly` shorthand is not registered in mise's tool registry.
:::

## Development checkout (working ON charly)

The same checkout above is the development checkout. Build and run the binary from the worktree
rather than installing it:

```bash
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

## Next

[Build your first box →](/start/quickstart/)
