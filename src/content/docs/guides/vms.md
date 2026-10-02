---
title: Virtual machines
description: charly's libvirt guests as a deploy substrate — how a VM is sourced, built and witnessed.
sidebar:
  order: 5
---

A VM is one of charly's deploy substrates, alongside the pod and local targets. `charly vm` is the
lifecycle verb — `build`, `create`, `start`, `stop`, `destroy`, `console`, `ssh`, `snapshot`,
`gpu`, `import`, `clone`, `cp-box`, `list` ([vm](/reference/cli/vm/)). It is served by the
compiled-in `plugin-vm` candy, whose handlers own the libvirt/qemu engine in-process and reach the
host only over generic seams.

## How a VM is sourced

A `vm:` node describes one guest, and its `source:` is a closed discriminated union keyed on
`kind` — a typo in the kind or in any of its fields is a validation error, not a silent fallback.
The schema models seven source kinds:

| `source.kind` | What it is |
|---|---|
| `cloud_image` | `url` is the guest rootfs image; `distro` selects the guest's package manager, sshd unit and package names. |
| `bootc` | `box` is a bootable container image laid onto a disk; `transport` and `rootfs` pick how it lands. |
| `clone` | `from_vm` + `from_snapshot` clone an existing guest, optionally re-running cloud-init. |
| `imported` | adopts an existing `libvirt_name` + `disk_path`/`disk_format` instead of building one. |
| `bootstrap` | `builder` + `distro` build a disk from the guest's own package manager. |
| `iso` | `url` is an INSTALLER medium, not a disk — charly allocates a blank disk and renders the distro's answer-file format from `installer:`. |
| `container_disk` | `image` is an OCI artifact carrying a bootable disk (the KubeVirt containerDisk contract, by default `/disk/disk.img`); charly pulls the layer and boots it through the unchanged libvirt/qemu path. |

The distinction that matters most: on `cloud_image` the `url` IS the rootfs, while on `iso` the
`url` boots an installer that partitions a separate disk. Everything downstream — the answer file,
the partition geometry, the account — follows from that.

## Beds that witness VMs

The VM beds declared across the release repositories each prove one sourcing path end to end:

| Bed | Owning repo | What it exercises |
|---|---|---|
| `check-arch-vm` | distro-arch | the Arch cloud-image guest (SPICE socket + virtio-gpu + qemu-guest-agent), and nested local-target deploys over the external VM deploy |
| `check-vm-clone` | distro-cachyos | the `clone` source — deploy a base at its golden snapshot, then boot and probe the clone |
| `check-omarchy-iso-vm` | distro-omarchy | unattended install from Omarchy's own official ISO, then assertions on the installed system |
| `check-cua-container-disk-vm` | distro-omarchy | the `container_disk` source — pull Cua's published Fleet containerDisk and boot it locally, no KubeVirt |
| `check-cachyos-gpu-vm` | distro-cachyos | VFIO GPU passthrough — a bare-metal KDE seat plus a nested streaming pod with real NVENC |

Each is `disposable: true`, which is what authorizes charly to destroy and rebuild the deployment
unattended — see [disposability is the license](/concepts/09-disposability-is-the-license/).

## Rootless

charly's nested VM work targets the rootless libvirt session, `qemu:///session`, which keys off
`$XDG_RUNTIME_DIR` and needs no `CAP_SYS_ADMIN`.

## GPU passthrough and the arbiter

GPU passthrough is a genuinely exclusive resource, so it goes through the resource arbiter. The
compiled-in `plugin-preempt` candy owns `verb:arbiter` — the exclusive/shared lease logic, the
crash-safe lease ledger, and the VFIO-to-NVIDIA driver-mode math — with
`charly preempt status` / `charly preempt restore` as its operator CLI
([preempt](/reference/cli/preempt/)).

The GPU passthrough bed claims the physical device with `requires_exclusive: [nvidia-gpu]`: before
it brings up its VM, the arbiter gracefully stops any running *preemptible* holder of that token —
for example an operator's GPU workstation whose per-host overlay marks it
`preemptible: {holds: [nvidia-gpu]}` — and restores it after teardown. The token is a portable
name, so on a host with no preemptible holder the arbiter finds nothing to preempt and the bed
still runs.

One rootless-specific gotcha: VFIO pins all guest RAM, so a `qemu:///session` domain needs a
memlock limit at least as large as the guest's RAM. The login-session default is far too low, and
the failure surfaces as a cryptic "cannot limit locked memory" at start.

## See also

- **[The vm recipe](/recipes/vm/vm/)** — the entity, its fields and the plan grammar.
- **[The VM catalog](/recipes/vm/vms-catalog/)** — the authoring reference for `kind:vm` entities.
- **[The libvirt check verb](/recipes/check/libvirt/)** — list, info, screenshot, snapshots and the rest.
- **[The schema comes first](/concepts/07-the-schema-comes-first/)** — why `source:` is a closed union.
