# Recipe 04 — Proxmox Auditor

**Status:** ⚠️ Needs backend (PVE + API token) · **Book ref:** Chapter 5 (infrastructure hands), Recipe 4

The Proxmox MCP server, scoped to an **auditor-role API token**. Answers "which VMs haven't been touched in 90 days and how much RAM are they hoarding?" without opening the PVE UI.

## Run

```bash
cp .env.example .env      # PVE_HOST + auditor token (user@realm!tokenid=secret)
docker compose up -d
```

## Stanza

```json
{ "mcpServers": { "proxmox-auditor": {
    "url": "http://<docker-host>:9104/mcp" } } }
```

The port binds to **loopback only** by default, so `<docker-host>` is `localhost`. If your client runs on another machine, set `MCP_BIND_ADDR` in `.env` to this host's LAN IP and use that — see [SECURITY.md](../../SECURITY.md#ports).

## First question

*"Which VMs haven't been touched in 90 days and how much RAM are they hoarding?"*

## Scope notes

- **PVEAuditor role only** for week one — the kill-VM tool is exactly as real as it sounds (book, Ch. 5).
- Create the token under Datacenter → Permissions → API Tokens, for a dedicated user, no privilege separation unless you know you want it.
- Promote write capability deliberately, with a note in your menu-notes file — the Chapter 5 ceremony.
- PVE uses self-signed certs by default; if the server supports a `VERIFY_TLS=false` escape hatch, prefer installing your CA over disabling verification.
