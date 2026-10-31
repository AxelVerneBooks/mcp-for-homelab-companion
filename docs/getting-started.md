# Getting started in 10 minutes

One recipe, end to end: from `git clone` to asking your assistant a question that gets answered by an MCP server you're running yourself. We'll use **Recipe 10 — The Custom Front Desk**. It ships its own mock backend (a pretend pool controller), so you don't need Home Assistant, Proxmox or anything else running.

> This repo is the free companion to [_MCP for the Homelab_](https://axelverne.com) by Axel Verne. The book covers the why behind every step below (transports, scoping, the security model). This page covers the how.

## What you need (1 min)

- **Docker** with the **Compose v2** plugin. Run `docker compose version` to check; anything from the last couple of years is fine.
- **An MCP client** that can connect to an HTTP (`url`) server, e.g. Claude Desktop, Claude Code, or any other MCP-capable app.
- Free TCP port **9110** on the Docker host.

## 1. Clone and step into the recipe (1 min)

```bash
git clone https://github.com/AxelVerneBooks/mcp-for-homelab-companion.git
cd mcp-for-homelab-companion/recipes/10-custom-front-desk
cp .env.example .env    # nothing to edit: the mock backend needs no settings
```

## 2. Bring it up and wait for health (3 min, mostly the first build)

```bash
docker compose up -d --build --wait
```

Two containers start: `pool-api` (the mock vendor API) and `pool-mcp` (your MCP server on `:9110`). `--wait` returns only when both pass their healthchecks. Check them with `docker compose ps`; both should say `healthy`.

## 3. Prove it speaks MCP (1 min)

Do a raw handshake with curl:

```bash
curl -s http://localhost:9110/mcp \
  -H 'Content-Type: application/json' -H 'Accept: application/json, text/event-stream' \
  -d '{"jsonrpc":"2.0","id":1,"method":"initialize","params":{"protocolVersion":"2025-06-18","capabilities":{},"clientInfo":{"name":"curl","version":"0"}}}'
```

You should get an `event: message` line whose JSON contains `"serverInfo":{"name":"pool",...}`.

To go further and call a tool end to end, which proves the MCP server can reach its backend, run the probe CI uses. It's plain Python 3 with no dependencies. From the repo root:

```bash
python3 tools/mcp_probe.py --http http://localhost:9110/mcp --call get_pool_status
```

```
    ✓ initialize — pool 1.x (protocol 2025-06-18)
    ✓ tools/list — 2 tools: get_pool_status, list_pool_sensors
    ✓ tools/call get_pool_status — { "water_temp_c": 27.2, "heater": "on", ... }
```

## 4. Wire your client (2 min)

Add this stanza to your client's MCP config. It's a `url` stanza because this server speaks streamable HTTP, not stdio:

```json
{ "mcpServers": { "pool": {
    "url": "http://localhost:9110/mcp" } } }
```

If the client runs on a different machine from Docker, replace `localhost` with the Docker host's name or IP. Then restart the client so it picks up the new server.

## 5. Ask the first question (1 min)

> *"Is the pool heater on, and how does the water temp compare to the solar intake reading?"*

The assistant should call `get_pool_status` and `list_pool_sensors` and answer from the readings. The mock randomizes values, so you'll get different numbers each time you ask. Nothing can change state: the only write tool (`set_pump_mode`) ships commented out in [`server.py`](../recipes/10-custom-front-desk/server.py).

## 6. Tear down (when you're done)

```bash
docker compose down
```

## If something goes wrong

| Symptom | Likely cause / fix |
|---|---|
| `Bind for 0.0.0.0:9110 failed: port is already allocated` | Something else holds 9110. Stop it, or change the left side of `"9110:9110"` (and your stanza). |
| `up --wait` fails with a container `unhealthy` | `docker compose logs pool-mcp`. On first build this is usually a network hiccup during `pip install`; re-run the command. |
| curl hangs or gets `connection refused` | Run `docker compose ps`. The container exiting immediately is the classic stdio-in-a-container bug; see the note at the bottom of `server.py`. |
| Client shows the server but no tools | You used a `command` stanza instead of `url`, or forgot to restart the client. |

## Next

- **Read [`server.py`](../recipes/10-custom-front-desk/server.py).** It's about 60 lines and covers the whole wrap-anything pattern. Then follow "Going real" in the [recipe README](../recipes/10-custom-front-desk/README.md) to point it at a real API.
- **Try Recipe 01** (read-only media librarian, stdio, no backend) to see the other transport.
- **Pick a backend recipe** (03–09) for a service you actually run, and follow the general ritual in the [top-level README](../README.md#the-general-ritual-every-recipe-every-time).
