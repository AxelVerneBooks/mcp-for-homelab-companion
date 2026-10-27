# Recipe 10 — The Custom Front Desk (Your Service Here)

**Status:** ✅ Works OOTB (mock backend baked in) · **Book ref:** Chapter 6, Recipe 10

The only recipe that ships its own backend: a **mock pool-controller API** stands in for the vendor's cloud service, so you can run, query, and *read the source* of a complete MCP wrap before aiming it at anything real.

## Run

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

The port binds to **loopback only** by default, so `<docker-host>` is `localhost`. If your client runs on another machine, set `MCP_BIND_ADDR` in `.env` to this host's LAN IP and use that — see [SECURITY.md](../../SECURITY.md#ports).

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
