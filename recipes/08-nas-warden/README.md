# Recipe 08 — NAS Health Warden

**Status:** ⚠️ Needs backend (TrueNAS + API key) · **Book ref:** Chapter 5 (infrastructure hands), Recipe 8

The TrueNAS SCALE MCP server — pool health, disk temps, dataset usage. Read-only, full stop.

## Run

```bash
cp .env.example .env      # TN_URL (websocket) + read-only API key
docker compose up -d
```

## Stanza

```json
{ "mcpServers": { "nas-warden": {
    "url": "http://<docker-host>:9108/mcp" } } }
```

## First question

*"How is the pool, and is any disk running hotter than its siblings?"*

## Scope notes

- **Read-only API key, full stop.** Storage servers are where a fat-fingered "cleanup" tool earns a chapter in a different book (book, Ch. 5).
- Create the key under Credentials → Users (API Keys) for a dedicated user.
- The websocket URL (`wss://`) is the usual failure point — make sure your reverse proxy passes websocket upgrades if you front TrueNAS.
