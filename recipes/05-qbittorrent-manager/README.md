# Recipe 05 — qBittorrent Night Manager

**Status:** ⚠️ Needs backend (qBit + account) · **Book ref:** Chapter 5 (library hands), Recipe 5

📖 **Read the chapter:** [_MCP for the Homelab_, Chapter 5](https://axelverne.com): library hands, the dedicated-account scope, and the same-host rule. All ten recipes are also in the Recipe Appendix (Chapter 10).

The qBittorrent MCP server. The killer tool isn't adding torrents — it's 2 a.m. diagnostics: *"why is nothing downloading."*

## Run

```bash
cp .env.example .env      # QBIT_URL + dedicated account
docker compose up -d
```

## Stanza

```json
{ "mcpServers": { "qbit-manager": {
    "url": "http://<docker-host>:9105/mcp" } } }
```

## First question

*"Why is nothing downloading — check the queue and any stalled transfers."*

## Scope notes

- **Dedicated qBit account**, never yours — qBit's permission model is coarse, so the account is the scope (book, Ch. 5).
- The server runs on the **same host/network as qBit** and is network-exiled from everything else (`qbit-net` only).
- Same-host rule from the book: credentials for qBit should never leave the segment qBit lives on.
