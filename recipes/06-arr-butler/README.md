# Recipe 06 — Radarr Butler (the *arr pattern)

**Status:** ⚠️ Needs backend (Radarr + API key) · **Book ref:** Chapter 5 (library hands), Recipe 6

## Overview

Radarr via MCP — and the **pattern for the whole *arr family**: Sonarr, Prowlarr, Lidarr are the same compose file with a different image, port, and API key. Served over streamable HTTP on port `9106`.

## Requirements

- Docker with Compose.
- Radarr reachable at `ARR_URL` (example: `http://radarr:7878`).
- `ARR_KEY`: the Radarr API key (Settings → General → Security).
- Image `arr-mcp:vX.Y.Z` — placeholder tag; pin the current release of the community arr-mcp.

## Quick start

```bash
cp .env.example .env      # ARR_URL + API key (Settings → General → Security)
docker compose up -d
```

For Sonarr/Prowlarr/Lidarr, duplicate the service with the family's MCP server image, a new container/port, and that app's API key.

## Stanza

```json
{ "mcpServers": { "radarr-butler": {
    "url": "http://<docker-host>:9106/mcp" } } }
```

## First question

*"What's sitting in Radarr's queue, and what's been stuck longest?"*

## Scope notes

- **Read-only until the couch-grab day** — promoting "find and grab the 4K remake" write access is the Chapter 5 ceremony, complete with a menu-notes entry.
- One server per *arr app; never share one server across apps via multiple keys — the menu gets muddy and the audit gets impossible.
- API keys are per-app: Settings → General → Security in each app's UI.

## Troubleshooting

- **Container starts and errors immediately** — `.env` isn't filled in; set `ARR_URL` and `ARR_KEY`.
- **Key rejected** — API keys are per-app; make sure `ARR_KEY` came from the same app `ARR_URL` points at.
- **Mixed-up answers across *arr apps** — run one server per app, never one server with several keys.
- **`vX.Y.Z` image not found** — the tag is a placeholder; pin a real release.

## License

MIT — see the [root LICENSE](../../LICENSE). Copyright (c) 2026 Axel Verne. Part of the free companion to [_MCP for the Homelab_](https://axelverne.com).
