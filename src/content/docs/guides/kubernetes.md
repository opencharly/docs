---
title: Kubernetes
description: charly's kubernetes deploy target and its witnesses — kind on three engines, k3s in a VM, and the KubeVirt platform.
sidebar:
  order: 6
---

`kubernetes:` is a deploy **target** — a YAML key on a deploy node — not a verb. There is no
`kubernetes` command word. The cluster work happens through `charly deploy`
([deploy](/reference/cli/deploy/)) and the `kube:` check verb
([check-k8s](/recipes/kubernetes/check-k8s/)).

## The deploy target

A `kubernetes:` deploy node is name-first and stays target-agnostic: it describes what the
workload needs (kind, replica, resources, exposure, storage, probes), while its `from:` cross-ref
points at a `kind: kubernetes` cluster template — the `kubernetes:` entity — that supplies the
Kubernetes-specific knobs (storage class, ingress class, cert issuer, secret backend).

`target: kubernetes` resolves OUT-OF-PROCESS to `plugin-kube`'s `deploy:kubernetes` provider. The
host generates an egress-validated Kustomize `base/` + `overlays/` tree and the out-of-process
plugin runs `kubectl apply -k` against it. Because every box runtime contract is baked into OCI
labels at build time, a Kubernetes deploy is possible from a pushed image alone — no `charly.yml`
required.

The recipe page [kubernetes](/recipes/kubernetes/kubernetes/) owns the full schema: the deploy
node fields, the three-layer build/capabilities/deployment model, and the generated-manifest
commands.

## Local clusters with kind

A local-cluster sibling reuses the same Kustomize + `kubectl` machinery without a remote cluster:
`kindcluster` (`kind: kindcluster`) provisions a local Kubernetes-in-Docker cluster with the
upstream `kind` tool, served by the `deploy:kindcluster` provider beside `deploy:kubernetes` in
`plugin-kube` ([kind](/recipes/kubernetes/kind/)).

kind provisions its node containers on the operator's own container engine, and charly's engine
word maps 1:1 to kind's `KIND_EXPERIMENTAL_PROVIDER`. Three disposable beds witness the three
engines — podman (`check-kindcluster`), docker (`check-kindcluster-docker`) and rootless nerdctl
(`check-kindcluster-nerdctl`) — differing only in `engine:` and a collision-free cluster name and
kubeconfig context, since a kind cluster name is unique only within an engine.

## k3s runs in a VM, not a pod

The remote path is a real k3s control plane in a disposable libvirt VM, not a pod. A VM's native
kernel and cgroup tree sidesteps the rootless-podman cpuset-delegation blocker that makes a
pod-hosted k3s impossible. The kubeconfig is pulled back over the auto-allocated `:6443` forward,
so the host-side `kube:` probes reach the guest's cluster directly.

## The KubeVirt platform

`check-kubevirt-operator` installs the KubeVirt and CDI operators and their CRs on a disposable
k3s VM, using the guest's own `kubectl` against the guest's own kubeconfig, then asserts the
platform: the `VirtualMachine` and `VirtualMachineInstance` CRDs are Established, the
`virt-handler` DaemonSet is Ready, and both the KubeVirt and CDI CRs report Deployed. The bed
proves the platform install end to end; booting a guest through KubeVirt is a separate concern.

## Beds

Every bed below is declared in charly's own `charly.yml`:

| Bed | What it proves |
|---|---|
| `check-k8s-deploy` | the externalized `deploy:kubernetes` substrate end to end — a k3s VM control plane plus a `target: kubernetes` workload applied to it |
| `check-k8s-deploy-app` | the minimal base box the substrate deploys (a disposable-bed fixture, not a production image) |
| `check-k8s-deploy-workload` | the `target: kubernetes` deploy of that fixture, with the host-generated Kustomize tree applied `-k` |
| `check-k3s-vm` | k3s in a disposable libvirt VM, and the full 13-method `kube:` probe surface against a real control plane |
| `check-helm-vm` | the out-of-tree `plugin-helm` path — a real chart installed with `helm` and asserted via `verb:helm` |
| `check-kubevirt-operator` | the KubeVirt + CDI platform install on a disposable k3s VM |
| `check-kindcluster` | kind on the podman engine |
| `check-kindcluster-docker` | kind on the docker engine |
| `check-kindcluster-nerdctl` | kind on the rootless nerdctl engine |
| `check-kindcluster-workload` | the `deploy:kindcluster` workload leg — a locally-built image loaded into the kind node and applied through the shared Kustomize generator |
| `check-kindcluster-lock` | teardown lock inheritance — a kindcluster root with a deploy-level member, torn down together |
| `check-kind-host-vm` | the kind-host profile applied into a disposable eval-vm guest, off the operator's workstation |

The `kube:` probe surface has 13 methods — `nodes`, `wait-nodes`, `pods`, `wait-ready`, `ingress`,
`ingressclass`, `storageclass`, `service`, `lb-external-ip`, `addons`, `apply`, `delete`, `raw` —
served out-of-process with a vendored client-go, so no external `kubectl` is needed to probe.

## See also

- **[The kubernetes recipe](/recipes/kubernetes/kubernetes/)** — the deploy schema and the three-layer model.
- **[The kind recipe](/recipes/kubernetes/kind/)** — the tool and its per-engine host preconditions.
- **[The kube check verb](/recipes/kubernetes/check-k8s/)** — the full cluster-probe surface.
- **[The helm recipe](/recipes/kubernetes/helm/)** — deploying a chart with `helm`.
