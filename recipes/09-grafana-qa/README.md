# Recipe 09 — Grafana Question Answerer

**Status:** ⚠️ Needs backend (Grafana + viewer token) · **Book ref:** Chapter 5 (Recipe 9)

## Overview

The Grafana MCP server — lets the assistant read dashboards and answer *"what does the last hour of CPU look like, and does it correlate with anything else on that dashboard?"* The correlation question is where it shines. Served over streamable HTTP on port `9109`.

## Requirements

- Docker with Compose.
- Grafana reachable at `GRAFANA_URL` (example: `http://grafana.local:3000`).
- `GRAFANA_TOKEN`: a service-account token holding the **Viewer** role (Administration → Users → Service accounts).
- Image `grafana-mcp:vX.Y.Z` — placeholder tag; pin the current release of the grafana MCP server.

## Quick start

```bash
cp .env.example .env      # GRAFANA_URL + Viewer-role service account token
docker compose up -d
```

## Stanza

```json
{ "mcpServers": { "grafana-qa": {
    "url": "http://<docker-host>:9109/mcp" } } }
```

## First question

*"What does the last hour of CPU look like on the hypervisor, and does it correlate with anything else on that dashboard?"*

## Scope notes

- **Viewer role only** — create a service account (Administration → Users → Service accounts) and a token for it; the Viewer role can read every dashboard but touch nothing.
- This is the recipe that multiplies the value of every other one: metrics + tool state = the assistant noticing what you'd miss.
- Keep dashboards for graphs; keep MCP for questions. (Book, Ch. 8: the dashboards become the archive, not the interface.)

## Troubleshooting

- **Container starts and errors immediately** — `.env` isn't filled in; set `GRAFANA_URL` and `GRAFANA_TOKEN`.
- **Dashboards missing or access denied** — the token must belong to a service account with the Viewer role (Administration → Users → Service accounts).
- **`vX.Y.Z` image not found** — the tag is a placeholder; pin a real release.

## License

MIT — see the [root LICENSE](../../LICENSE). Copyright (c) 2026 Axel Verne. Part of the free companion to [_MCP for the Homelab_](https://axelverne.com).
