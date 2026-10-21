# Recipe 05 — qBittorrent Night Manager

**Status:** ⚠️ Needs backend (qBit WebUI) · **Transport:** SSE (legacy) · **Book ref:** Chapter 5 (library hands), Recipe 5

[qbittorrent-mcp-rs](https://github.com/nicholaswilde/qbittorrent-mcp-rs), a small Rust MCP server for qBittorrent. The killer tool isn't adding torrents. It's 2 a.m. diagnostics: *"why is nothing downloading."*

| | |
|---|---|
| Image | `nicholaswilde/qbittorrent-mcp-rs:0.3.9` (amd64, arm64, arm/v7) |
| Needs | qBittorrent with WebUI enabled, on a Docker network this container can join |
| Endpoint | `http://<docker-host>:9105/sse` with `Authorization: Bearer <QBIT_MCP_TOKEN>` |
| Writes | Present in the menu (add/delete/pause). Gate them with your client's approval prompt. |

## Setup

1. **Find qBit's Docker network** (the server talks to qBit over it, not over your LAN):

   ```bash
   docker inspect qbittorrent -f '{{range $k, $v := .NetworkSettings.Networks}}{{$k}} {{end}}'
   ```

2. **Configure and start:**

   ```bash
   cd recipes/05-qbittorrent-manager
   cp .env.example .env
   $EDITOR .env        # QBIT_HOST/PORT/USER/PASS, QBIT_NETWORK, QBIT_MCP_TOKEN=$(openssl rand -hex 32)
   docker compose config -q
   docker compose up -d
   ```

3. **Prove the endpoint answers:**

   ```bash
   curl -sN -m 3 http://localhost:9105/sse -H "Authorization: Bearer <QBIT_MCP_TOKEN>"
   ```

   Expected: `event: endpoint` followed by `data: /message?session_id=…`. A `401` means a wrong token. If `up` fails with *network … not found*, `QBIT_NETWORK` is wrong.

4. Add the stanza, restart your client, ask the first question.

## Stanza (SSE, not streamable HTTP)

```json
{ "mcpServers": { "qbit-manager": {
    "type": "sse",
    "url": "http://<docker-host>:9105/sse",
    "headers": { "Authorization": "Bearer <QBIT_MCP_TOKEN>" } } } }
```

Clients that only speak streamable HTTP need a bridge such as `mcp-remote`. This server has no `/mcp` endpoint.

## First question

*"Why is nothing downloading? Check the queue and troubleshoot any stalled torrent."*

## Scope notes

- **qBittorrent has exactly one WebUI login.** There is no "dedicated, limited account" to create, so whoever holds these credentials holds the whole client. Rotate the password after setup.
- **The network is the scope** (book, Ch. 5): the server joins only qBit's network, and qBit's credentials never cross your LAN.
- **The bearer token is required.** Compose refuses to start without `QBIT_MCP_TOKEN`, and without it the endpoint answers `401`.
- **Lazy mode is a menu trim, not a lock.** The server starts out showing only `list_torrents` and `show_all_tools`. One call to `show_all_tools` reveals the full menu, including `delete_torrent`, `set_app_preferences` and `shutdown_app`. Keep your client's per-tool approval on for anything that isn't a read.
- **Env-var quirk (v0.3.9):** upstream documents `QBITTORRENT_HOST`, but that key is ignored for a single instance. The compose file uses the working `QBITTORRENT_QBITTORRENT_*` names, which were checked against the source.

## Tested

During this audit the exact compose file ran against a real `linuxserver/qbittorrent:5.3.0` container on a shared network. SSE `initialize` succeeded, `list_torrents` returned live data, and unauthenticated requests got `401`.
