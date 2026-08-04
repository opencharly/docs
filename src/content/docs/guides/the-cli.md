---
title: The charly CLI
description: How the command surface is put together — a small core spine and a large plugin-served catalog.
sidebar:
  order: 3
---

`charly` is one binary with a large command surface, and almost none of it is in the binary's own
source. Understanding that split makes the [CLI reference](/reference/cli/bundle/) easier to read.

## A small spine, a large catalog

Three top-level words are the **core spine**, implemented by the binary itself:

| Word | What it is |
|---|---|
| `charly box` | the build/authoring parent — its subcommands are plugin-served |
| `charly version` | the CalVer identity of the running binary |
| `charly reap-orphans` | internal cleanup of orphaned resources |

Everything else — `bundle`, `check`, `secrets`, `candy`, `alias`, `agent`, `clean`, `status`,
`shell`, `vm`, `config` and the rest — is a **command word served by a plugin candy**. Each has a
page in the [CLI reference](/reference/cli/bundle/) naming the plugin that serves it and whether
that plugin is compiled into the binary or loaded at runtime.

Some plugin-served words nest under a parent: `add-candy`, `generate`, `list`, `new`, `pkg`,
`validate` and friends are children of `charly box`. The nesting is expressed in the plugin's Go
code rather than its manifest, so the reference pages name the word and its owner without
asserting where it sits — run `charly box --help` for the live tree.

## Getting live help

The generated pages here describe *what serves a word and why*. For the exact flags of a given
invocation, ask the binary:

```bash
charly bundle add --help
charly box build --help
```

:::note[A wrinkle worth knowing]
For a plugin-served word, `charly <word> --help` is answered by the host and shows a generic
stub. The plugin's own grammar appears one level deeper (`charly bundle add --help`) or via the
bare form (`charly bundle help`). This is also why this site's CLI reference is generated from
each plugin's declarations rather than scraped from help output — the help surface is not
uniform enough to parse.
:::

## Driving it from an agent

The same binary is an MCP server, so every verb is reachable over RPC. `mcp` is itself an
out-of-process command plugin, discovered from the project's `candy/plugin-mcp` rather than
compiled in — so run it from inside a project that provides it, or it exits 80:

```bash
git clone https://github.com/opencharly/charly && cd charly
charly mcp serve
```

An agent authoring a candy uses the same commands you would — `charly candy set`,
`charly candy add-rpm`, `charly box write` — with comments and key order preserved across edits.

## See also

- **[CLI reference](/reference/cli/bundle/)** — one page per command word.
- **[Provider index](/reference/providers/)** — every reserved word, including non-command classes.
