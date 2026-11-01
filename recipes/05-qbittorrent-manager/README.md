# Recipe 05 — qBittorrent Night Manager

**Status:** ⚠️ Needs backend (qBit + account) · **Book ref:** Chapter 5 (library hands), Recipe 5

## Overview

The qBittorrent MCP server. The killer tool isn't adding torrents — it's 2 a.m. diagnostics: *"why is nothing downloading."* Served over streamable HTTP on port `9105`.

## Requirements

- Docker with Compose.
- qBittorrent with the WebUI enabled, reachable at `QBIT_URL` (example: `http://qbittorrent:8080`).
- A **dedicated** qBit account for the assistant: `QBIT_USER` / `QBIT_PASS`.
- The existing Docker network your qBit container uses, named `qbit-net` (declared `external: true` in the compose file).
- Image `qbit-mcp:vX.Y.Z` — placeholder tag; pin the current release of the community qbit-mcp.

## Quick start

```bash
cp .env.example .env      # QBIT_URL + dedicated account
docker compose up -d
```

## Stanza

```json
{ "mcpServers": { "qbit-manager": {
    "url": "http://<docker-host>:9105/mcp" } } }
```

## First question

*"Why is nothing downloading — check the queue and any stalled transfers."*

## Scope notes

- **Dedicated qBit account**, never yours — qBit's permission model is coarse, so the account is the scope (book, Ch. 5).
- The server runs on the **same host/network as qBit** and is network-exiled from everything else (`qbit-net` only).
- Same-host rule from the book: credentials for qBit should never leave the segment qBit lives on.

## Troubleshooting

- **`docker compose up` complains the network doesn't exist** — `qbit-net` is external; it must be the network your qBit container actually uses. Point the compose file at that network.
- **Can't reach qBit** — `QBIT_URL` must resolve on `qbit-net`, and the qBit WebUI must be enabled.
- **Container starts and errors immediately** — `.env` isn't filled in; set `QBIT_URL`, `QBIT_USER`, `QBIT_PASS`.
- **`vX.Y.Z` image not found** — the tag is a placeholder; pin a real release.

## License

MIT — see the [root LICENSE](../../LICENSE). Copyright (c) 2026 Axel Verne. Part of the free companion to [_MCP for the Homelab_](https://axelverne.com).
