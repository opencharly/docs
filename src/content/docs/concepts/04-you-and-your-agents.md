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

Expose the whole CLI over RPC:

```bash
charly mcp serve                 # Streamable HTTP or stdio
charly mcp serve --read-only     # filters the destructive tools out
```

Author a candy the way an agent would — the same verbs you would use by hand, with comments and
key order preserved across every edit:

```bash
charly box new candy my-tool
charly candy add-rpm my-tool ripgrep
charly candy set my-tool env.MY_VAR value
charly box add-candy tutorial-shell my-tool
charly -C box/fedora box validate
```

And when the agent wants to know whether its change worked, it runs what you would run:

```bash
charly -C box/fedora check run tutorial-shell-dev
```

## If you know MCP

The server is generated, not curated. Each leaf command becomes a tool with its flags as the input
schema, so the tool list is exactly the CLI. `--read-only` filters by the command's own
destructiveness rather than by an allowlist someone maintains, and containers can additionally
provide their own MCP servers, auto-discovered by consumers through the `mcp_provide:` declaration.

## See also

- **[The charly CLI](/guides/the-cli/)** — the command surface and how plugins serve it.
- **[The MCP command](/recipes/build/charly-mcp-cmd/)** — the gateway in detail.
- **[The spec is the test](/concepts/06-the-spec-is-the-test/)** — what an agent grades against.
