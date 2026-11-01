# Recipe 04 — Proxmox Auditor

**Status:** ⚠️ Needs backend (PVE + API token) · **Book ref:** Chapter 5 (infrastructure hands), Recipe 4

## Overview

The Proxmox MCP server, scoped to an **auditor-role API token**. Answers "which VMs haven't been touched in 90 days and how much RAM are they hoarding?" without opening the PVE UI. Served over streamable HTTP on port `9104`.

## Requirements

- Docker with Compose.
- A Proxmox VE node reachable at `PVE_HOST` (example: `https://pve.local:8006`).
- `PVE_TOKEN`: an API token with the **PVEAuditor** role, format `user@realm!tokenid=secret` (Datacenter → Permissions → API Tokens).
- `VERIFY_TLS` (defaults to `true`).
- Image `proxmox-mcp:vX.Y.Z` — placeholder tag; pin the current release of the community proxmox-mcp.

## Quick start

```bash
cp .env.example .env      # PVE_HOST + auditor token (user@realm!tokenid=secret)
docker compose up -d
```

## Stanza

```json
{ "mcpServers": { "proxmox-auditor": {
    "url": "http://<docker-host>:9104/mcp" } } }
```

## First question

*"Which VMs haven't been touched in 90 days and how much RAM are they hoarding?"*

## Scope notes

- **PVEAuditor role only** for week one — the kill-VM tool is exactly as real as it sounds (book, Ch. 5).
- Create the token under Datacenter → Permissions → API Tokens, for a dedicated user, no privilege separation unless you know you want it.
- Promote write capability deliberately, with a note in your menu-notes file — the Chapter 5 ceremony.
- PVE uses self-signed certs by default; if the server supports a `VERIFY_TLS=false` escape hatch, prefer installing your CA over disabling verification.

## Troubleshooting

- **Container starts and errors immediately** — `.env` isn't filled in; set `PVE_HOST` and `PVE_TOKEN`.
- **Token rejected** — check the format `user@realm!tokenid=secret` and that the token's user has the PVEAuditor role.
- **TLS / certificate errors** — PVE uses self-signed certs by default. Prefer installing your CA over setting `VERIFY_TLS=false`.
- **`vX.Y.Z` image not found** — the tag is a placeholder; pin a real release.

## License

MIT — see the [root LICENSE](../../LICENSE). Copyright (c) 2026 Axel Verne. Part of the free companion to [_MCP for the Homelab_](https://axelverne.com).
