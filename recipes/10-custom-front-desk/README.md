# Recipe 10 — The Custom Front Desk (Your Service Here)

**Status:** ✅ Works OOTB (mock backend baked in) · **Transport:** streamable HTTP · **Book ref:** Chapter 6, Recipe 10

The only recipe that ships its own backend: a **mock pool-controller API** stands in for the vendor's cloud service, so you can run, query, and *read the source* of a complete MCP wrap before aiming it at anything real.

| | |
|---|---|
| Images | built locally from `python:3.14.8-slim`, with `mcp==1.30.0`, `httpx==0.28.1`, `uvicorn==0.54.0`, `fastapi==0.156.5` |
| Needs | Docker. Nothing else. |
| Endpoint | `http://<docker-host>:9110/mcp` |
| Writes | `set_pump_mode` ships commented out (see the source) |

## Setup

```bash
cd recipes/10-custom-front-desk
docker compose config -q
docker compose up -d --build
curl -s http://localhost:9110/mcp -X POST \
  -H 'Content-Type: application/json' -H 'Accept: application/json, text/event-stream' \
  -d '{"jsonrpc":"2.0","id":1,"method":"initialize","params":{"protocolVersion":"2025-11-25","capabilities":{},"clientInfo":{"name":"curl","version":"0"}}}'
```

Expected: `event: message` and a `data:` line with `"serverInfo":{"name":"pool",…}`. Then add the stanza, restart your client, and ask the first question. `docker compose down` when you're done.

## Stanza

```json
{ "mcpServers": { "pool": {
    "url": "http://<docker-host>:9110/mcp" } } }
```

## First question

*"Is the pool heater on, and how does the water temp compare to the solar intake reading?"*

## Read the source — it's the chapter

- [server.py](server.py) — the entire pattern: docstrings are the menu, signatures are the schema, scope is enforced in code, and the **write tool ships commented out** with the three-step promotion checklist.
- [mock-api.py](mock-api.py) — two routes standing in for a vendor API.

**Why `mcp==1.30.0` and not 2.x:** the MCP Python SDK 2.x renamed `FastMCP` to `MCPServer` and moved `host`/`port` from the constructor to `run()`. `server.py` follows the book's FastMCP code, so it stays on the newest 1.x release. Port it when you're ready ([migration guide](https://py.sdk.modelcontextprotocol.io/v2/migration/)).

## Going real (the 30-minute path)

1. Delete the `pool-api` service, and the `depends_on: [pool-api]` line, from the compose file.
2. `cp .env.example .env`, uncomment and set `POOL_API_URL` and `POOL_API_KEY` to the vendor's.
3. `docker compose up -d --build`, re-run the curl above, and wire the stanza.
4. Week of clean reads → uncomment `set_pump_mode` per the checklist in the source.

## Tested

`tools/smoke.sh` builds this stack, completes the MCP `initialize` handshake, and calls `get_pool_status` through a full session, checking that the reply carries the mock API's `water_temp_c`.
