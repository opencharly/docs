---
title: You and your agents
description: One command surface, reachable from a shell or over RPC — with no second-class channel.
sidebar:
  order: 4
---

> **Two tasters at one bench.** The same `charly` surface serves you at the keyboard and your
> agents driving the line, with no second-class channel for either. Built for you *and* your
> agents, in the same breath.
>
> — [tenet 4](/vision/)

## The idea

Tools that grow an agent story usually grow a second, smaller surface for it — a handful of
endpoints wrapping the parts someone judged safe to automate. That surface then lags: it is
maintained separately, it lacks the newest verbs, and the agent ends up shelling out anyway.

Here there is one surface. The `charly` binary is also an MCP server, and every leaf command is
exposed as an MCP tool by reflection over the same command model the CLI uses. Nothing is
hand-listed, so nothing can lag: a new verb is reachable over RPC the moment it exists.

That symmetry is what makes the rest of this site's claims hold for both readers. When a page says
"prove it on a disposable bed", the agent runs the identical command you would — same verbs, same
exit codes, same output. There is no automation dialect to learn and no capability that exists
only at the keyboard.

Authoring is part of the same surface, and it is the part that matters most for an agent. Editing
YAML by regenerating it destroys comments and key order; charly's editor verbs go through the YAML
*node* API instead, so a machine edit leaves a human-authored file intact.

## In practice

Expose the whole CLI over RPC — from inside a project, since `mcp` is an out-of-process command
plugin that charly loads from the project's own `candy/plugin-mcp`:

```bash
git clone https://github.com/opencharly/charly && cd charly

charly mcp serve                 # Streamable HTTP or stdio
charly mcp serve --read-only     # filters the destructive tools out
```

Run outside a project that provides the plugin, `charly mcp serve` exits 80 — the verb is not
compiled into the binary, it is discovered.

Author a candy the way an agent would — the same verbs you would use by hand, with comments and
key order preserved across every edit:

```bash
git clone https://github.com/opencharly/distro-fedora && cd distro-fedora

charly box new candy my-tool
charly candy add-rpm my-tool ripgrep
charly candy set my-tool env.MY_VAR value
charly box add-candy tutorial-shell my-tool
charly box validate
```

Every verb here writes to the project in the current directory, so the sequence runs against a
clone you own. `--repo` is the read-only counterpart — it resolves a published project into a
cache, and a scaffold in your working directory is invisible to it, so the two never mix.

And when the agent wants to know whether its change worked, it runs what you would run:

```bash
charly --repo opencharly/distro-fedora check run check-tutorial-shell
```

## If you know MCP

The **tool list** is generated, not curated. Each leaf command becomes a tool with its flags as the
input schema, so the catalogue is exactly the CLI and cannot lag behind it.

The **destructive classification is not** generated — it is an explicit, hand-maintained list of
mutating tool paths (the lifecycle, config, secrets, deploy, build, VM and settings families).
Destructive tools are registered with a `DestructiveHint` annotation and left in place, on the
assumption that the client runtime acts on the hint; `--read-only` skips registering them entirely,
which is the setting to use for an untrusted or network-exposed deployment. Worth knowing that the
list is maintained by hand: a genuinely new mutating verb is safe only once it has been added to it.

Containers can additionally provide their own MCP servers, auto-discovered by consumers through the
`mcp_provide:` declaration.

## See also

- **[The charly CLI](/guides/the-cli/)** — the command surface and how plugins serve it.
- **[The MCP command](/recipes/build/charly-mcp-cmd/)** — the gateway in detail.
- **[The spec is the test](/concepts/06-the-spec-is-the-test/)** — what an agent grades against.
