# Recipe 12 — Uptime Kuma Sentinel

**Status:** ⚠️ Needs backend (Uptime Kuma 2.x + login) · **Book ref:** Chapter 5 pattern (infrastructure eyes), beyond the appendix

The Uptime Kuma MCP server — monitors, heartbeats, uptime percentages, and incident history as questions instead of a wall of green tiles. The question that sells it: *"what flapped overnight, and did those flaps line up?"*

**Image:** `davidfuchs/mcp-uptime-kuma:0.12.1` (pinned; streamable HTTP on `/mcp`). **Uptime Kuma 2.x only.**

## Run

```bash
cp .env.example .env      # UPTIME_KUMA_URL + login
docker compose up -d
```

## Verify

```bash
docker compose ps                 # kuma-mcp: running, not restarting
docker compose logs kuma-mcp      # should show a successful login to Kuma, no auth errors
curl -s http://127.0.0.1:9112/mcp -X POST \
  -H 'Content-Type: application/json' -H 'Accept: application/json, text/event-stream' \
  -d '{"jsonrpc":"2.0","id":1,"method":"initialize","params":{"protocolVersion":"2026-07-28","capabilities":{},"clientInfo":{"name":"curl","version":"0"}}}'
```

Expect a body containing `"serverInfo"`. Then confirm it is **not** reachable from another machine: `curl -m 3 http://<docker-host>:9112/mcp` from your laptop must fail to connect.

## Stanza

Run your MCP client on the Docker host, or tunnel to it (`ssh -L 9112:127.0.0.1:9112 <docker-host>`):

```json
{ "mcpServers": { "kuma-sentinel": {
    "url": "http://127.0.0.1:9112/mcp" } } }
```

## First question

*"Which monitors went down in the last 24 hours, for how long, and did any of them fail at the same time?"*

## Scope notes

- **The endpoint is unauthenticated** (upstream says so plainly) and **Kuma has no read-only role** — the MCP server holds full admin. That's why the compose file binds `127.0.0.1` only; widening that port binding is a bug, not a convenience.
- Pausing monitors, editing them, and maintenance windows are write tools. Week one: ask questions only. A paused monitor is a silent outage you created.
- If Kuma 2FA is on, the server supports a 2FA token — but a dedicated login is cleaner than sharing yours. Kuma is single-user, so "dedicated" here means a strong unique password rotated when you retire this recipe.
- Env names track the pinned release; re-check them against the upstream README when you bump the tag.
