# Recipe 07 — Pi-hole Query Detective

**Status:** ⚠️ Needs backend (Pi-hole + token) · **Book ref:** Chapter 5 (network hands), Recipe 7

The Pi-hole MCP server. Answers *"which client made the most blocked queries in the last 24 hours?"* — half of the Chapter 2 "why is the Wi-Fi weird" investigation.

## Run

```bash
cp .env.example .env      # PIHOLE_URL + read-only token
docker compose up -d
```

## Stanza

```json
{ "mcpServers": { "pihole-detective": {
    "url": "http://<docker-host>:9107/mcp" } } }
```

The port binds to **loopback only** by default, so `<docker-host>` is `localhost`. If your client runs on another machine, set `MCP_BIND_ADDR` in `.env` to this host's LAN IP and use that — see [SECURITY.md](../../SECURITY.md#ports).

## First question

*"Which client made the most blocked queries in the last 24 hours?"*

## Scope notes

- **Read-only token.** "Disable blocking for 5 minutes" is the tool that tempts everyone; it stays behind the approval click forever (book, Ch. 5).
- Pi-hole v6 changed the auth model (app-password/session vs. the old CLI token) — pin a server release matching your Pi-hole major version.
- The best pairing is recipes 07 + the router recipe: query logs + client state = the full "did the network change" answer.
