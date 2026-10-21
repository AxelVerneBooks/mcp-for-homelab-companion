# Recipe 06 — Radarr Butler (the *arr pattern)

**Status:** ⚠️ Needs backend (Radarr + API key) · **Transport:** streamable HTTP · **Book ref:** Chapter 5 (library hands), Recipe 6

Radarr via [mcp-arr](https://github.com/aplaceforallmystuff/mcp-arr), and the **pattern for the whole *arr family**: Sonarr, Lidarr and Prowlarr use the same image with a different service name, port and `*_URL` / `*_API_KEY` pair.

| | |
|---|---|
| Image | `ghcr.io/aplaceforallmystuff/mcp-arr:1.7.3` |
| Needs | Radarr v5+ and its API key |
| Endpoint | `http://localhost:9106/mcp` (loopback by default, see below) |
| Writes | `radarr_add_movie`, `radarr_update_movie`, `radarr_search_movie`, `radarr_refresh_movie`, `radarr_delete_queue_item`. Gate them with your client's approval prompt |

## Setup

```bash
cd recipes/06-arr-butler
cp .env.example .env
$EDITOR .env          # ARR_URL as seen from the container, ARR_KEY from Settings → General → Security
docker compose config -q
docker compose up -d
```

**Prove the endpoint answers:**

```bash
curl -s http://localhost:9106/mcp -X POST \
  -H 'Content-Type: application/json' -H 'Accept: application/json, text/event-stream' \
  -d '{"jsonrpc":"2.0","id":1,"method":"initialize","params":{"protocolVersion":"2025-11-25","capabilities":{},"clientInfo":{"name":"curl","version":"0"}}}'
```

Expected: `"serverInfo"` in the reply. Then add the stanza, restart your client, and ask the first question.

> **`ARR_URL` from inside a container:** `http://radarr:7878` only works if both containers share a Docker network. Otherwise use the Docker host's LAN IP, e.g. `http://192.168.1.20:7878`.

## Stanza

```json
{ "mcpServers": { "radarr-butler": {
    "url": "http://localhost:9106/mcp" } } }
```

## First question

*"What's sitting in Radarr's queue, and what's been stuck longest?"*

## The *arr pattern: adding Sonarr

```yaml
  sonarr-mcp:
    image: ghcr.io/aplaceforallmystuff/mcp-arr:1.7.3
    environment: { MCP_TRANSPORT: http, HOST: 0.0.0.0, PORT: "3000",
                   SONARR_URL: "${SONARR_URL}", SONARR_API_KEY: "${SONARR_KEY}" }
    ports: ["${MCP_BIND:-127.0.0.1}:9116:3000"]
    restart: unless-stopped
```

## Scope notes

- **No caller authentication.** mcp-arr has no bearer token, so anyone who can reach the port can drive Radarr. That's why the port binds to `127.0.0.1` unless you set `MCP_BIND`. If the client runs on another machine, set `MCP_BIND` to the host's LAN IP *on a trusted segment*, or put an authenticating reverse proxy in front.
- **Reads until the couch-grab day.** *arr API keys are all-or-nothing and this server has no read-only switch. Until you've done the Chapter 5 promotion ceremony (with a menu-notes entry), keep your client's per-tool approval on for the five write tools in the table above.
- **One server per *arr app.** Never share one server across apps via multiple keys: the menu gets muddy and the audit gets impossible.

## Tested

During this audit, mcp-arr 1.7.3 (the same release, from npm) ran in HTTP mode against a real `linuxserver/radarr:6.4.4` container. `radarr_get_health` and `radarr_get_queue` returned live data. The GHCR image tag was checked for existence; this sandbox can't pull GHCR layers.
