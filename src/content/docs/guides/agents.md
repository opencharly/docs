---
title: Agents and the control plane
description: Driving charly from an agent — the MCP bridge, the agent control plane, and the marketplace corpus.
sidebar:
  order: 7
---

charly is built to be driven by an agent as well as by a person. That shows up in three places:
the binary is itself an MCP server, the agent control plane is a first-class command family, and
the marketplace ships a skill corpus for several harnesses.

## The binary is an MCP server

`charly mcp serve` speaks the Model Context Protocol; `mcp` is served out-of-process by the
`plugin-mcp` candy ([mcp](/reference/cli/mcp/)). The tool surface is built from the host's own CLI
model, so the RPC set follows the project you point charly at rather than a fixed list.

The package ships systemd units named `charly-mcp`, in both system and user scope:

```yaml
systemd:
    - name: charly-mcp
      scope: system
      exec: /usr/bin/charly mcp serve --listen 127.0.0.1:18765
      description: Charly MCP server (Streamable HTTP on 127.0.0.1:18765)
      restart: on-failure
    - name: charly-mcp
      scope: user
      exec: /usr/bin/charly mcp serve --listen 127.0.0.1:18765
      description: Charly MCP server (user session, Streamable HTTP on 127.0.0.1:18765)
      restart: on-failure
```

They are **installed but never enabled** — nothing starts at boot; the operator starts one on
demand with `systemctl start charly-mcp` or `systemctl --user start charly-mcp`. On the host the
server binds loopback only; `--listen 0.0.0.0:18765` is the explicit opt-in, normal inside a
pod or VM deployment.

## The agent control plane

`plugin-agent` owns the CUE-validated `agent` and `agent-team` kinds plus three command words:

| Verb | What it is |
|---|---|
| `charly agent` | the headless, daemon-free agent control CLI — sessions, runs, ordered evidence, incidents, RCA and recovery decisions ([agent](/reference/cli/agent/)) |
| `charly tui` | the terminal UI for the same control plane — browse and drive sessions, runs and terminal channels interactively ([tui](/reference/cli/tui/), [recipe](/recipes/agent/tui/)) |
| `charly tmux` | a typed compatibility facade preserving the legacy tmux command grammar; it never constructs remote tmux shell strings ([tmux](/reference/cli/tmux/)) |

Everything routes through generic provider channels, so charly never reaches into an operator's
tmux socket.

## The rest of the agent surface

| Verb | What it is |
|---|---|
| `charly pipeline` | the domain-neutral agent/workflow engine — run a declared plan, the bare agent runtime, deterministic probes, template rendering ([pipeline](/reference/cli/pipeline/), [recipe](/recipes/pipeline/pipeline/)) |
| `charly review` | the PR-review engine: it assembles the complete PR context (body, every changed file's unified diff, commits, comment thread) into one model call and emits a deterministic `PASS`/`BLOCK` verdict ([review](/reference/cli/review/)) |
| `charly feature` | the project-inspection surface — enumerate a project's plan-shaped entity descriptions (`list` / `pending` / `validate`) ([feature](/reference/cli/feature/)) |
| `charly task` | a named, host-native reusable plan authored as a `task:` node using the same step grammar a candy's `plan:` uses ([task](/reference/cli/task/)) |
| `charly agentteams` | the management CLI for the AgentTeams controller REST API plus the declarative `agentteams:` check verb ([agentteams](/reference/cli/agentteams/)) |

## The marketplace corpus

The [marketplace](https://github.com/opencharly/marketplace) ships a skill corpus for several
agent harnesses. Its README names Claude Code (and Cursor, which reads the same `.claude-plugin`
catalog), Codex CLI (via the `.agents` catalog), Kimi Code, and pi.

Skills are addressed as `/charly-<plugin>:<skill>` — for example a plugin family plus one of its
skill names — and this site publishes that corpus under
[recipes](/recipes/), one page per skill plus its reference detail pages.

## See also

- **[You and your agents](/concepts/04-you-and-your-agents/)** — the concept behind the control plane.
- **[The CLI](/guides/the-cli/)** — the core spine versus the plugin-served catalog.
- **[Install](/start/install/)** — installing the packages that carry the `charly-mcp` units.
