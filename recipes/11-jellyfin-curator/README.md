# Recipe 11 — Jellyfin Curator

**Status:** ⚠️ Needs backend (Jellyfin + API key) · **Book ref:** Chapter 5 pattern (library hands), beyond the appendix

The Jellyfin MCP server — recipe 01 can see your files; this one sees what Jellyfin *thinks* of them: watch history, unmatched items, half-finished series, who's streaming right now. The first demo is *"what did we start and never finish?"*

**Image:** `ghcr.io/jaredtrent/jellyfin-mcp:2026.604.2` (pinned; streamable HTTP on `/mcp`, health on `/health`).

## Run

```bash
cp .env.example .env      # JELLYFIN_URL + dedicated API key + your bearer token
docker compose up -d
```

## Verify

```bash
docker compose ps                                   # jellyfin-mcp: running, not restarting
curl -sf http://localhost:9111/health && echo OK    # server is up
source .env && curl -s http://localhost:9111/mcp -X POST \
  -H "Authorization: Bearer $MCP_HTTP_TOKEN" \
  -H 'Content-Type: application/json' -H 'Accept: application/json, text/event-stream' \
  -d '{"jsonrpc":"2.0","id":1,"method":"initialize","params":{"protocolVersion":"2026-07-28","capabilities":{},"clientInfo":{"name":"curl","version":"0"}}}'
```

Expect a body containing `"serverInfo"`. Repeat the curl **without** the `Authorization` header — it must be refused (401). If it isn't, stop: the token isn't wired.

## Stanza

```json
{ "mcpServers": { "jellyfin-curator": {
    "url": "http://<docker-host>:9111/mcp",
    "headers": { "Authorization": "Bearer <MCP_HTTP_TOKEN>" } } } }
```

## First question

*"Which series did we start in the last six months and abandon before the halfway mark?"*

## Scope notes

- **Jellyfin API keys are admin-grade** — there is no read-only key. The scope is therefore (a) a dedicated key you can revoke alone, (b) the bearer token in front of the server, and (c) `jellyfin-mcp-net`, which shares nothing with the rest of your stack.
- Week one is reads only: library, playback history, sessions. Library refreshes and metadata edits are write tools — promote them deliberately (book, Ch. 5/6), never because a demo asked.
- Never point this at a Jellyfin that's exposed to the internet with the same key your reverse proxy uses.
- If the container exits immediately, check `docker compose logs` — a missing `HTTP_TOKEN` or unreachable `JELLYFIN_URL` is the usual (and intended) loud failure. Env names track the pinned release; re-check them against the upstream README when you bump the tag.
