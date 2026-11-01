# Recipe 03 — Home Assistant Concierge

**Status:** ⚠️ Needs backend (HA + token) · **Book ref:** Chapter 5 (environment hands), Recipe 3

## Overview

The Home Assistant MCP server — the one that converts skeptics, because the first demo is *"dim the office lights and start the movie scene"* typed from the couch. Served over streamable HTTP on port `9103`.

## Requirements

- Docker with Compose.
- Home Assistant reachable at `HASS_URL` (example: `http://homeassistant.local:8123`).
- `HASS_TOKEN`: a long-lived access token created under a **dedicated** HA user's profile — never your personal token.
- Image `ha-mcp:vX.Y.Z` — placeholder tag; pin the current release of the community HA MCP server.

## Quick start

```bash
cp .env.example .env      # HASS_URL + HASS_TOKEN for a DEDICATED user
docker compose up -d
```

## Stanza

```json
{ "mcpServers": { "ha-concierge": {
    "url": "http://<docker-host>:9103/mcp" } } }
```

## First question

*"Run the movie scene and tell me what it actually changed."*

## Scope notes

- **Dedicated HA user** whose permissions are "areas you'd let a houseguest touch" (book, Ch. 5). The MCP token must not be your personal token.
- Locks, alarm panels, and garage doors stay off the menu — verify the *user's* permission list, not just the server's tool list; scoping at the hub inherits downward.
- Long-lived access token, created in HA under the dedicated user's profile.

## Troubleshooting

- **Container starts and errors immediately** — `.env` isn't filled in. That's the designed failure mode (loud, early, honest); set `HASS_URL` and `HASS_TOKEN` and `docker compose up -d` again.
- **The assistant can touch things it shouldn't** — check the dedicated HA user's permissions, not the server's tool list; scoping at the hub inherits downward.
- **`vX.Y.Z` image not found** — the tag is a placeholder; pin a real release.

## License

MIT — see the [root LICENSE](../../LICENSE). Copyright (c) 2026 Axel Verne. Part of the free companion to [_MCP for the Homelab_](https://axelverne.com).
