# Recipe 03 — Home Assistant Concierge

**Status:** ⚠️ Needs backend (HA + token) · **Transport:** streamable HTTP · **Book ref:** Chapter 5 (environment hands), Recipe 3

[ha-mcp](https://github.com/homeassistant-ai/ha-mcp), the community Home Assistant MCP server. This is the one that converts skeptics: the first demo is *"what's on in the living room?"* typed from the couch, and on promotion day, *"start the movie scene."*

| | |
|---|---|
| Image | `ghcr.io/homeassistant-ai/ha-mcp:8.7.0` |
| Needs | Home Assistant + a long-lived token for a dedicated, non-admin user |
| Endpoint | `http://<docker-host>:9103/<MCP_SECRET_PATH>` |
| Writes | Off for week one (`READ_ONLY_MODE=true`): hidden from the menu *and* blocked at call time |

## Setup

1. **In Home Assistant:** Settings → People → Users → *Add user* (e.g. `mcp-concierge`), **not** an administrator. Log in as that user once, then Profile → Security → *Long-lived access tokens* → *Create token*.
2. **Configure:**

   ```bash
   cd recipes/03-ha-concierge
   cp .env.example .env
   $EDITOR .env        # HASS_URL, HASS_TOKEN, and MCP_SECRET_PATH=$(openssl rand -hex 24)
   docker compose config -q
   docker compose up -d
   docker compose logs -f ha-mcp     # watch for HA connection errors; Ctrl-C when quiet
   ```

3. **Prove the endpoint answers** (replace `<secret>` with your `MCP_SECRET_PATH`):

   ```bash
   curl -s http://localhost:9103/<secret> -X POST \
     -H 'Content-Type: application/json' -H 'Accept: application/json, text/event-stream' \
     -d '{"jsonrpc":"2.0","id":1,"method":"initialize","params":{"protocolVersion":"2025-11-25","capabilities":{},"clientInfo":{"name":"curl","version":"0"}}}'
   ```

   Expected: an SSE `data:` line containing `"serverInfo"`. A `404` means the path is wrong.

4. Add the stanza, restart your client, ask the first question.

## Stanza

```json
{ "mcpServers": { "ha-concierge": {
    "url": "http://<docker-host>:9103/<MCP_SECRET_PATH>" } } }
```

## First question

*"Which lights are on right now, and what would the movie scene change?"*

## Scope notes

- **Dedicated, non-admin HA user.** The MCP token must not be your personal token. Be clear-eyed about what that buys: HA has no per-entity permissions, so a non-admin user can still call services on any entity. What it removes is the admin surface (config, add-ons, users, restarts).
- **Read-only first.** With `READ_ONLY_MODE=true`, ha-mcp lists about 40 read tools instead of about 77 and refuses write calls at execution time. Promote (`READ_ONLY_MODE=false`, `docker compose up -d`) only after a clean week, with a menu-notes entry (book, Ch. 5).
- **True houseguest scoping:** if you want "only these lights and the TV, never the locks", use Home Assistant's **built-in** MCP Server integration instead (Settings → Devices & services → *Model Context Protocol Server*). It needs no container and only sees entities you've exposed to Assist (Settings → Voice assistants → *Expose*). Stanza: `"url": "http://homeassistant.local:8123/api/mcp"` with `"headers": {"Authorization": "Bearer <token>"}`.
- **The secret path is the only gate** on this endpoint. Generate it, keep it out of screenshots, and don't port-forward 9103.

## Tested

During this audit, ha-mcp 8.7.0 was started in HTTP mode with these exact settings. It answered `initialize` on the secret path, returned `404` on any other path, and listed 40 tools with `READ_ONLY_MODE=true` against 77 without it. A live Home Assistant was not available, so tool calls against real entities are untested here.
