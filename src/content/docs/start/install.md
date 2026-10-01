---
title: Install
description: Install the charly CLI from the signed package repositories (or the release binary via mise) and put it on your $PATH.
sidebar:
  order: 1
---

**Install `charly` once, then use it from anywhere.** The rest of this site is written for a
machine with `charly` installed and no charly checkout anywhere: `--repo <owner>/<repo>` reads a
published project straight from git, and `charly box new project <dir>` starts one of your own.
Nothing on any other page asks you to clone a repository.

`charly` runs on Linux, `amd64` and `arm64`. The native packages pull in their runtime
dependencies — podman for containers, qemu/libvirt for VMs, gocryptfs for encrypted volumes.

## Install from the package repositories

Every package is signed. On `arm64`, replace `amd64` with `arm64` in the repository URLs.

### Fedora

Create `/etc/yum.repos.d/charly.repo`:

```ini
[charly]
name=charly
baseurl=https://opencharly.github.io/charly-fedora/amd64
enabled=1
gpgcheck=1
gpgkey=https://opencharly.github.io/charly-fedora/RPM-GPG-KEY-charly
```

```bash
sudo dnf install charly
```

### Debian and Ubuntu

On Ubuntu, use `charly-ubuntu` in place of `charly-debian`:

```bash
curl -fsSL https://opencharly.github.io/charly-debian/charly.gpg | sudo gpg --dearmor -o /etc/apt/keyrings/charly.gpg
echo "deb [signed-by=/etc/apt/keyrings/charly.gpg] https://opencharly.github.io/charly-debian/ stable main" | sudo tee /etc/apt/sources.list.d/charly.list
sudo apt update
sudo apt install charly
```

### Arch Linux and CachyOS

```bash
curl -fsSL -o /tmp/charly.gpg https://opencharly.github.io/charly-arch/charly.gpg
sudo pacman-key --add /tmp/charly.gpg
sudo pacman-key --lsign-key 978DFF11A951A830F7ADA2D4062B073E9D1BAE2E
```

Append to `/etc/pacman.conf`, then install:

```ini
[charly]
Server = https://opencharly.github.io/charly-arch/amd64
SigLevel = Required
```

```bash
sudo pacman -Sy charly
```

### Alpine

```bash
sudo wget -O /etc/apk/keys/charly.rsa.pub https://opencharly.github.io/charly-alpine/charly.rsa.pub
echo "https://opencharly.github.io/charly-alpine/amd64" | sudo tee -a /etc/apk/repositories
sudo apk update
sudo apk add charly
```

### Variants

Each repository carries three packages:

| Package | What it bakes in |
|---|---|
| `charly` | the everyday set: secrets, feature, vm, doctor, clean, settings, candy, mcp, review, pipeline |
| `charly-full` | the everyday set plus GPU udev rules and the preemption arbiter |
| `charly-minimal` | doctor, clean, settings |

There is also an [OpenWrt feed](https://github.com/opencharly/charly-openwrt) — the binary installs
and runs there, but OpenWrt carries no podman or libvirt — and a build for the
[JetKVM appliance](https://github.com/opencharly/charly-jetkvm).

### Check the install

```bash
charly version   # the CalVer the binary was stamped with
charly doctor    # what is installed, what is missing, which GPU charly sees
```

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
tells you which one. A release binary brings no runtime dependencies with it; `charly doctor`
reports what is missing.

:::note[Why `github:opencharly/charly`?]
mise's GitHub backend (`github:org/repo`) installs release assets from GitHub Releases — the
modern replacement for the deprecated `ubi:` backend. The full backend spec is what resolves; a
bare `charly` shorthand is not registered in mise's tool registry.
:::

## Developing charly

All development on charly itself happens in the umbrella repository,
[opencharly/opencharly](https://github.com/opencharly/opencharly) — one clone of the whole org,
with charly, the plugins, the distros and this site pinned as submodules:

```bash
git clone --recurse-submodules https://github.com/opencharly/opencharly.git
cd opencharly
./charly/scripts/bootstrap-charly.sh   # builds ./charly/bin/charly (CalVer-stamped) — never installs it
```

Never edit a submodule in place. Each session works in its own git worktree under
`.worktrees/<slug>/<repo>/`, branched off `origin/main`, builds its own binary there, and lands
every change by pull request. The umbrella's
[AGENTS.md](https://github.com/opencharly/opencharly/blob/main/AGENTS.md) has the full development
model.

:::caution[Use the binary you just built]
A stale `bin/charly` is the classic way to waste an afternoon — it can fail in confusing ways
that look like real bugs. If anything behaves strangely, re-run `scripts/bootstrap-charly.sh` in
your worktree and check `charly version` against it before investigating further.
:::

To start your own project, create a `charly.yml` and a `candy/` directory in any directory.
Projects predating the current schema convert in one shot with `charly migrate`, a single
idempotent pass to the latest CalVer schema.

## Next

[Build your first box →](/start/quickstart/)
