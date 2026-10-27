# Recipe 03 — Home Assistant Concierge

**Status:** ⚠️ Needs backend (HA + token) · **Book ref:** Chapter 5 (environment hands), Recipe 3

The Home Assistant MCP server — the one that converts skeptics, because the first demo is *"dim the office lights and start the movie scene"* typed from the couch.

## Run

```bash
cp .env.example .env      # HASS_URL + HASS_TOKEN for a DEDICATED user
docker compose up -d
```

## Stanza

```json
{ "mcpServers": { "ha-concierge": {
    "url": "http://<docker-host>:9103/mcp" } } }
```

The port binds to **loopback only** by default, so `<docker-host>` is `localhost`. If your client runs on another machine, set `MCP_BIND_ADDR` in `.env` to this host's LAN IP and use that — see [SECURITY.md](../../SECURITY.md#ports).

## First question

*"Run the movie scene and tell me what it actually changed."*

## Scope notes

- **Dedicated HA user** whose permissions are "areas you'd let a houseguest touch" (book, Ch. 5). The MCP token must not be your personal token.
- Locks, alarm panels, and garage doors stay off the menu — verify the *user's* permission list, not just the server's tool list; scoping at the hub inherits downward.
- Long-lived access token, created in HA under the dedicated user's profile.
