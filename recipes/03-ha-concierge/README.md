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

## First question

*"Run the movie scene and tell me what it actually changed."*

## Scope notes

- **Dedicated HA user** whose permissions are "areas you'd let a houseguest touch" (book, Ch. 5). The MCP token must not be your personal token.
- Locks, alarm panels, and garage doors stay off the menu — verify the *user's* permission list, not just the server's tool list; scoping at the hub inherits downward.
- Long-lived access token, created in HA under the dedicated user's profile.

---

From the free, MIT-licensed companion repo for [_MCP for the Homelab_](https://axelverne.com) by Axel Verne. The book covers this recipe in Chapter 5, Recipe 3. Back to the [recipe catalog](https://axelvernebooks.github.io/mcp-for-homelab-companion/).
