# Recipe 08 — NAS Health Warden

**Status:** ⚠️ Needs backend (TrueNAS + API key) · **Book ref:** Chapter 5 (infrastructure hands), Recipe 8

## Overview

The TrueNAS SCALE MCP server — pool health, disk temps, dataset usage. Read-only, full stop. Served over streamable HTTP on port `9108`.

## Requirements

- Docker with Compose.
- TrueNAS SCALE with its websocket endpoint at `TN_URL` (example: `wss://truenas.local/websocket`).
- `TN_KEY`: a **read-only** API key for a dedicated user (Credentials → Users → API Keys).
- Image `truenas-mcp:vX.Y.Z` — placeholder tag; pin the current release of the community truenas-mcp.

## Quick start

```bash
cp .env.example .env      # TN_URL (websocket) + read-only API key
docker compose up -d
```

## Stanza

```json
{ "mcpServers": { "nas-warden": {
    "url": "http://<docker-host>:9108/mcp" } } }
```

## First question

*"How is the pool, and is any disk running hotter than its siblings?"*

## Scope notes

- **Read-only API key, full stop.** Storage servers are where a fat-fingered "cleanup" tool earns a chapter in a different book (book, Ch. 5).
- Create the key under Credentials → Users (API Keys) for a dedicated user.
- The websocket URL (`wss://`) is the usual failure point — make sure your reverse proxy passes websocket upgrades if you front TrueNAS.

## Troubleshooting

- **Can't connect to TrueNAS** — the websocket URL is the usual failure point. Use the `wss://…/websocket` form, and if a reverse proxy fronts TrueNAS, make sure it passes websocket upgrades.
- **Container starts and errors immediately** — `.env` isn't filled in; set `TN_URL` and `TN_KEY`.
- **`vX.Y.Z` image not found** — the tag is a placeholder; pin a real release.

## License

MIT — see the [root LICENSE](../../LICENSE). Copyright (c) 2026 Axel Verne. Part of the free companion to [_MCP for the Homelab_](https://axelverne.com).
