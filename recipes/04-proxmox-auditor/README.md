# Recipe 04 — Proxmox Auditor

**Status:** ⚠️ Needs backend (PVE + API token) · **Transport:** streamable HTTP · **Book ref:** Chapter 5 (infrastructure hands), Recipe 4

[ProxmoxMCP-Plus](https://github.com/RekklesNA/ProxmoxMCP-Plus), scoped twice: an **auditor-role API token** on the Proxmox side, and a **read-only tool allowlist** on the server side. Answers "which VMs haven't been touched in 90 days and how much RAM are they hoarding?" without opening the PVE UI.

| | |
|---|---|
| Image | `ghcr.io/rekklesna/proxmoxmcp-plus:v0.6.6` |
| Needs | Proxmox VE 8+ and an API token for a dedicated user with `PVEAuditor` |
| Endpoint | `http://<docker-host>:9104/mcp` with `Authorization: Bearer <MCP_API_KEY>` |
| Writes | Hidden by `MCP_TOOL_ALLOWLIST` (26 read tools) *and* denied by the token's role |

## Setup

1. **In Proxmox** (Datacenter → Permissions):
   - *Users → Add*: `mcp-bot`, realm `pve`.
   - *API Tokens → Add*: user `mcp-bot@pve`, token ID `homelab`. Copy the secret; it is shown once.
   - *Permissions → Add → API Token Permission*: path `/`, token `mcp-bot@pve!homelab`, role **PVEAuditor**. If you leave *Privilege Separation* on, grant the role to the token itself (as here), not only the user.
2. **Configure and start:**

   ```bash
   cd recipes/04-proxmox-auditor
   cp .env.example .env
   $EDITOR .env        # PVE_* values, and MCP_API_KEY=$(openssl rand -hex 32)
   docker compose config -q
   docker compose up -d
   docker compose logs -f pve-mcp     # Ctrl-C once it says it is listening
   ```

3. **Prove the endpoint answers:**

   ```bash
   curl -s http://localhost:9104/mcp -X POST -H "Authorization: Bearer $(grep ^MCP_API_KEY .env | cut -d= -f2)" \
     -H 'Content-Type: application/json' -H 'Accept: application/json, text/event-stream' \
     -d '{"jsonrpc":"2.0","id":1,"method":"initialize","params":{"protocolVersion":"2025-11-25","capabilities":{},"clientInfo":{"name":"curl","version":"0"}}}'
   ```

   Expected: `"serverInfo":{"name":"ProxmoxMCP"...}`. A `401` means the bearer token doesn't match `MCP_API_KEY`.

4. Add the stanza, restart your client, ask the first question.

## Stanza

```json
{ "mcpServers": { "proxmox-auditor": {
    "url": "http://<docker-host>:9104/mcp",
    "headers": { "Authorization": "Bearer <MCP_API_KEY>" } } } }
```

## First question

*"Which VMs haven't been touched in 90 days and how much RAM are they hoarding?"*

## Scope notes

- **PVEAuditor role only** for week one. The stop/delete/migrate tools are exactly as real as they sound (book, Ch. 5).
- **Belt and braces:** `MCP_TOOL_ALLOWLIST` in the compose file lists only read tools. The server rejects unknown names at startup, so a typo fails loudly instead of widening access. Promoting a write tool means adding its name to that list *and* granting the token a role that allows it. Do both deliberately, with a menu-notes entry (the Chapter 5 ceremony).
- `get_cluster_join_info` is deliberately **not** allowlisted: it returns join secrets.
- PVE ships a self-signed cert. Prefer installing your CA (or a real cert) over `PVE_VERIFY_SSL=false`.
- `MCP_API_KEY` is required. The compose file refuses to start without it, because an unauthenticated Proxmox endpoint on your LAN is a bad day waiting.

## Tested

During this audit, ProxmoxMCP-Plus 0.6.6 was started with these exact env settings and an unreachable PVE host. It answered `initialize`, returned `401` without the bearer token, and listed exactly the 26 allowlisted tools. A live Proxmox node was not available, so tool calls against real VMs are untested here.
