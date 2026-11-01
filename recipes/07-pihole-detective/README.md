# Recipe 07 — Pi-hole Query Detective

**Status:** ⚠️ Needs backend (Pi-hole + token) · **Book ref:** Chapter 5 (network hands), Recipe 7

## Overview

The Pi-hole MCP server. Answers *"which client made the most blocked queries in the last 24 hours?"* — half of the Chapter 2 "why is the Wi-Fi weird" investigation. Served over streamable HTTP on port `9107`.

## Requirements

- Docker with Compose.
- Pi-hole v6 reachable at `PIHOLE_URL` (example: `http://pihole.local`).
- `PIHOLE_TOKEN`: an API token/password scoped for read-only use.
- Image `pihole-mcp:vX.Y.Z` — placeholder tag; pin a release matching your Pi-hole major version.

## Quick start

```bash
cp .env.example .env      # PIHOLE_URL + read-only token
docker compose up -d
```

## Stanza

```json
{ "mcpServers": { "pihole-detective": {
    "url": "http://<docker-host>:9107/mcp" } } }
```

## First question

*"Which client made the most blocked queries in the last 24 hours?"*

## Scope notes

- **Read-only token.** "Disable blocking for 5 minutes" is the tool that tempts everyone; it stays behind the approval click forever (book, Ch. 5).
- Pi-hole v6 changed the auth model (app-password/session vs. the old CLI token) — pin a server release matching your Pi-hole major version.
- The best pairing is recipes 07 + the router recipe: query logs + client state = the full "did the network change" answer.

## Troubleshooting

- **Auth fails** — Pi-hole v6 changed auth (session app-password vs. the old CLI token). Pin a server release matching your Pi-hole major version.
- **Container starts and errors immediately** — `.env` isn't filled in; set `PIHOLE_URL` and `PIHOLE_TOKEN`.
- **`vX.Y.Z` image not found** — the tag is a placeholder; pin a real release.

## License

MIT — see the [root LICENSE](../../LICENSE). Copyright (c) 2026 Axel Verne. Part of the free companion to [_MCP for the Homelab_](https://axelverne.com).
