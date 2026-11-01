# Recipe 10 — The Custom Front Desk (Your Service Here)

**Status:** ✅ Works OOTB (mock backend baked in) · **Book ref:** Chapter 6, Recipe 10

## Overview

The only recipe that ships its own backend: a **mock pool-controller API** stands in for the vendor's cloud service, so you can run, query, and *read the source* of a complete MCP wrap before aiming it at anything real.

- `pool-api` — the "vendor" API (mock, baked in): `GET /status`, `GET /sensors`.
- `pool-mcp` — your front desk: two read-only tools (`get_pool_status`, `list_pool_sensors`) over streamable HTTP on `:9110`.

## Requirements

- Docker with Compose (both images are built locally from `python:3.12-slim`).
- `curl` for the handshake check below.
- Nothing else for the OOTB path — no `.env` settings are required with the mock backend. `POOL_API_KEY` is only needed when you go real.

## Quick start

```bash
docker compose up -d --build
curl -s http://localhost:9110/mcp -X POST \
  -H 'Content-Type: application/json' -H 'Accept: application/json, text/event-stream' \
  -d '{"jsonrpc":"2.0","id":1,"method":"initialize","params":{"protocolVersion":"2026-07-28","capabilities":{},"clientInfo":{"name":"curl","version":"0"}}}'
```

## Stanza

```json
{ "mcpServers": { "pool": {
    "url": "http://<docker-host>:9110/mcp" } } }
```

## First question

*"Is the pool heater on, and how does the water temp compare to the solar intake reading?"*

## Read the source — it's the chapter

- [server.py](server.py) — the entire pattern: docstrings are the menu, signatures are the schema, scope is enforced in code, and the **write tool ships commented out** with the three-step promotion checklist.
- [mock-api.py](mock-api.py) — two routes standing in for a vendor API. Replace `POOL_API_URL` + `POOL_API_KEY` in `.env` to aim at the real thing.

## Going real (the 30-minute path)

1. Delete the `pool-api` service from the compose file.
2. `cp .env.example .env`, set `POOL_API_URL` and `POOL_API_KEY` to the vendor's.
3. Rebuild, re-run the curl above, and wire the stanza.
4. Week of clean reads → uncomment `set_pump_mode` per the checklist in the source.

## Troubleshooting

- **No answer on `:9110` right after `up`** — the first boot builds the images cold; give it up to ~30 seconds (the repo's `tools/smoke.sh` waits that long) and retry the curl.
- **Container exits instantly and silently** — `FastMCP.run()` defaults to stdio, and in a container stdin closes immediately. `server.py` calls `mcp.run(transport="streamable-http")` for that reason; keep it if you edit the file.
- **Still hitting the mock after going real** — `docker-compose.yml` sets `POOL_API_URL: http://pool-api:8080` directly on `pool-mcp`, so check that line as well as `.env` when you remove the `pool-api` service.
- **Smoke-test the whole repo** — `./tools/smoke.sh` from the repo root runs the same initialize handshake and reports pass/fail.

## License

MIT — see the [root LICENSE](../../LICENSE). Copyright (c) 2026 Axel Verne. Part of the free companion to [_MCP for the Homelab_](https://axelverne.com).
