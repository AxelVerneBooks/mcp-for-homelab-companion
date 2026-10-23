# Recipe 15 — Prometheus Analyst

**Status:** ⚠️ Needs backend (Prometheus) · **Book ref:** Chapter 8 pattern (questions over dashboards), beyond the appendix

The Prometheus MCP server — PromQL for people who don't want to write PromQL. Recipe 09 reads the dashboards you built; this one reads the metrics you *didn't* build dashboards for. The question that earns its keep: *"which scrape targets are down, and since when?"*

**Image:** `ghcr.io/pab1it0/prometheus-mcp-server:1.6.2` (pinned; HTTP transport on `:8080/mcp`, health on `/health`).

## Run

```bash
cp .env.example .env      # PROMETHEUS_URL (+ basic auth if your proxy needs it)
docker compose up -d
```

## Verify

```bash
docker compose ps                                   # prometheus-mcp: running, not restarting
curl -sf http://localhost:9115/health && echo OK    # server is up
source .env && curl -sf "$PROMETHEUS_URL/api/v1/query?query=up" | head -c 200; echo   # Prometheus answers
curl -s http://localhost:9115/mcp -X POST \
  -H 'Content-Type: application/json' -H 'Accept: application/json, text/event-stream' \
  -d '{"jsonrpc":"2.0","id":1,"method":"initialize","params":{"protocolVersion":"2026-07-28","capabilities":{},"clientInfo":{"name":"curl","version":"0"}}}'
```

Expect a body containing `"serverInfo"`.

## Stanza

```json
{ "mcpServers": { "prometheus-analyst": {
    "url": "http://<docker-host>:9115/mcp" } } }
```

## First question

*"Which scrape targets are down right now, since when, and is anything else on those hosts trending badly in the last six hours?"*

## Scope notes

- **Reads by construction** — the tools are query, range-query, metadata, and targets. Keep `--web.enable-admin-api` **off** on Prometheus; it's the only door to deletes, and nothing here needs it.
- The cost risk is load, not damage: an over-eager range query across a year of high-cardinality series can stall a small Prometheus. Set `--query.timeout` and `--query.max-samples` on Prometheus itself; that's the scope fence.
- Running more than one instance (e.g. homelab + cloud Prometheus)? The server supports a `TOOL_PREFIX` env so the two tool menus don't collide.
- Env names track the pinned release; re-check them against the upstream README when you bump the tag.
