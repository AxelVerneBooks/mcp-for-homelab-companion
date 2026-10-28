# Recipe 07 — Pi-hole Query Detective

**Status:** ⚠️ Needs backend (Pi-hole + token) · **Book ref:** Chapter 5 (network hands), Recipe 7

📖 **Read the chapter:** [_MCP for the Homelab_, Chapter 5](https://axelverne.com): network hands and why the disable-blocking tool always stays behind approval. All ten recipes are also in the Recipe Appendix (Chapter 10).

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

## First question

*"Which client made the most blocked queries in the last 24 hours?"*

## Scope notes

- **Read-only token.** "Disable blocking for 5 minutes" is the tool that tempts everyone; it stays behind the approval click forever (book, Ch. 5).
- Pi-hole v6 changed the auth model (app-password/session vs. the old CLI token) — pin a server release matching your Pi-hole major version.
- The best pairing is recipes 07 + the router recipe: query logs + client state = the full "did the network change" answer.
