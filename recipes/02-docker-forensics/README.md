# Recipe 02 — Docker Forensics

**Status:** ✅ Works OOTB (socket is local) · **Book ref:** Chapter 4 (Docker), Recipe 2

## Overview

The docker-mcp server scoped with `ALLOW_LIST` — the assistant can see and manage *only* the containers you name. This is the recipe that turns "list my containers" into a one-sentence question.

docker-mcp runs as a **stdio** server spawned by your client (see the stanza below). The compose file exists to *validate* the socket mount and env shape on your host, not to serve HTTP.

## Requirements

- Docker with Compose, on the host whose containers you're exposing (the socket path `/var/run/docker.sock` is host-local).
- Image `docker-mcp:vX.Y.Z` — placeholder tag; pin the current release.
- `ALLOW_LIST` in `.env`: the container names the assistant may see or touch, comma-separated, no spaces.

## Quick start

```bash
cp .env.example .env      # set ALLOW_LIST to your container names
docker compose run --rm socket-check  # validates socket visibility + env shape
```

## Stanza (stdio)

```json
{ "mcpServers": { "docker-forensics": {
    "command": "docker",
    "args": ["run", "--rm", "-i",
             "-v", "/var/run/docker.sock:/var/run/docker.sock",
             "--env-file", "<this folder>/.env",
             "docker-mcp:vX.Y.Z"] } } }
```

## First question

*"Which containers have restarted more than once this week, and why?"*

## Scope notes

- **The socket is root with a different hat** (book, Ch. 7 Rule 3). This is the *only* recipe in the repo that mounts it.
- `ALLOW_LIST` is the security boundary, not a suggestion. A container not in the list is invisible to the assistant — that's the design.
- Run this server on the host whose containers you're exposing; the socket path is host-local.

## Troubleshooting

- **`socket-check` fails** — `/var/run/docker.sock` isn't visible; you're probably not on the Docker host whose containers you want to expose.
- **A container is "missing"** — it isn't in `ALLOW_LIST`. That's the boundary working; add it deliberately (comma-separated, no spaces) if it belongs there. `socket-check` echoes the value it parsed.
- **Any other recipe asks for the Docker socket** — treat it as a bug; report it, don't run it.
- **`vX.Y.Z` image not found** — the tag is a placeholder; pin a real release.

## License

MIT — see the [root LICENSE](../../LICENSE). Copyright (c) 2026 Axel Verne. Part of the free companion to [_MCP for the Homelab_](https://axelverne.com).
