# Recipe 07 — Pi-hole Query Detective

**Status:** ⚠️ Needs backend (Pi-hole v6 + app password) · **Transport:** streamable HTTP · **Book ref:** Chapter 5 (network hands), Recipe 7

[pihole-mcp](https://github.com/hexamatic/pihole-mcp), a Go MCP server for the Pi-hole v6 API, locked to its read-only tool set. It answers *"which client made the most blocked queries in the last 24 hours?"*, which is half of the Chapter 2 "why is the Wi-Fi weird" investigation.

| | |
|---|---|
| Image | `ghcr.io/hexamatic/pihole-mcp:0.9.0` |
| Needs | Pi-hole **v6** (2025+ releases) and an app password |
| Endpoint | `http://<docker-host>:9107/mcp` with `Authorization: Bearer <PIHOLE_MCP_TOKEN>` |
| Writes | None: `PIHOLE_READ_ONLY=true` is fixed in the compose file (49 read tools; write tools don't exist) |

## Setup

1. **In Pi-hole:** Settings → Web interface / API → *Expert* mode → Advanced → **Configure app password**. Copy it. App passwords skip TOTP and can be revoked without changing your login.
2. **Configure and start:**

   ```bash
   cd recipes/07-pihole-detective
   cp .env.example .env
   $EDITOR .env      # PIHOLE_URL, PIHOLE_PASSWORD, PIHOLE_MCP_TOKEN=$(openssl rand -hex 32), MCP_HOSTNAME
   docker compose config -q
   docker compose up -d
   docker compose run --rm pihole-mcp -check    # connectivity + auth check against your Pi-hole, then exits
   ```

3. **Prove the endpoint answers:**

   ```bash
   curl -s http://localhost:9107/mcp -X POST -H 'Authorization: Bearer <PIHOLE_MCP_TOKEN>' \
     -H 'Content-Type: application/json' -H 'Accept: application/json, text/event-stream' \
     -d '{"jsonrpc":"2.0","id":1,"method":"initialize","params":{"protocolVersion":"2025-11-25","capabilities":{},"clientInfo":{"name":"curl","version":"0"}}}'
   ```

   Expected: `"serverInfo"`. A `401` means a wrong token. A `403` *"invalid Host"* means the host name in your URL isn't in `MCP_HOSTNAME`.

4. Add the stanza, restart your client, ask the first question.

## Stanza

```json
{ "mcpServers": { "pihole-detective": {
    "url": "http://<MCP_HOSTNAME>:9107/mcp",
    "headers": { "Authorization": "Bearer <PIHOLE_MCP_TOKEN>" } } } }
```

## First question

*"Which client made the most blocked queries in the last 24 hours?"*

## Scope notes

- **The lock is in the server, not the password.** Pi-hole has no read-only API users: an app password can do anything the web UI can. `PIHOLE_READ_ONLY=true` is hard-coded in the compose file (not in `.env`) so it can't drift. "Disable blocking for 5 minutes" is the tool that tempts everyone, and it stays out of the menu (book, Ch. 5).
- **v6 only.** Pi-hole v6 replaced the old `api.php` token with sessions and app passwords. This server speaks v6. For a v5 Pi-hole, upgrade Pi-hole first.
- **`MCP_HOSTNAME`** feeds the server's DNS-rebinding guard. It's not authentication; the bearer token is.
- **Best pairing:** this recipe + 09 (Grafana). Query logs plus network metrics gives the full "did the network change?" answer.

## Tested

During this audit, pihole-mcp v0.9.0 (built from the tagged source) ran against a real `pihole/pihole:2026.10.0` container. With read-only on it listed 49 tools, `pihole_stats_top_clients` returned live data, `pihole_dns_set_blocking` was "tool not found", and blocking stayed enabled. Over HTTP it returned `401` without the token and `403` for a Host header that isn't allowlisted. The GHCR image tag was checked for existence; this sandbox can't pull GHCR layers.
