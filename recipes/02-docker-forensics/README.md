# Recipe 02 — Docker Forensics

**Status:** ✅ Works OOTB (socket is local) · **Transport:** stdio · **Book ref:** Chapter 4 (Docker), Recipe 2

[mcp-server-docker](https://github.com/ckreiling/mcp-server-docker) behind a **read-only gate**: a [docker-socket-proxy](https://github.com/Tecnativa/docker-socket-proxy) that answers reads (list, inspect, logs, stats) and refuses every write with `403`. This is the recipe that turns "list my containers" into a one-sentence question, and "stop everything" into a polite error.

| | |
|---|---|
| Images | `tecnativa/docker-socket-proxy:v0.5.0` · `mcp-server-docker:0.3.0` (built locally from upstream tag `v0.3.0`; upstream publishes no image) |
| Needs | Docker, on the host whose containers you want to inspect. |
| Writes | Refused by the proxy (`POST=0`), whatever the server's menu says. |

## Setup

```bash
cd recipes/02-docker-forensics
cp .env.example .env                   # optional: turn API sections off (1 → 0)
docker compose config -q               # 1. the file is valid
docker compose up -d                   # 2. starts the read-only gate (socket-proxy)
docker compose run --rm gate-check     # 3. expect: two "allowed" reads, then "403 (gate holds)"
docker compose build docker-mcp        # 4. builds mcp-server-docker:0.3.0 from the pinned git tag
```

5. Add the stanza below, restart your client, ask the first question.

## Stanza (stdio)

The client spawns the server on the gate's private network. It never gets the socket, only `tcp://socket-proxy:2375`.

```json
{ "mcpServers": { "docker-forensics": {
    "command": "docker",
    "args": ["run", "--rm", "-i",
             "--network", "mcp-recipe-02-docker-ro",
             "-e", "DOCKER_HOST=tcp://socket-proxy:2375",
             "mcp-server-docker:0.3.0"] } } }
```

## First question

*"Which containers have restarted more than once this week, and why?"*

## Scope notes

- **The socket is root with a different hat** (book, Ch. 7 Rule 3). Only `socket-proxy` mounts it, and this is the *only* recipe in the repo that does.
- **The proxy is the security boundary.** `POST=0` makes every state-changing Docker API call (`start`, `stop`, `rm`, `pull`, `exec`, `run`) return `403`, so the server's write tools exist in its menu but cannot act. Don't "fix" those errors by flipping `POST`. That's the promotion ceremony (Chapter 5), not a config tweak.
- **Narrowing is per API section, not per container.** No Docker MCP server today enforces a container-name allowlist (the earlier `ALLOW_LIST` idea in this repo was never enforced by any real server, so it's gone). Use the `PROXY_*` switches in `.env` to hide whole sections (e.g. `PROXY_VOLUMES=0`). If some containers must stay invisible, run them on another Docker host.
- The `docker-ro` network is `internal: true`: the gate has no route out, and only containers you attach to it can reach it.

## Tested

`docker compose run --rm gate-check` is part of `tools/smoke.sh`. During this audit, `mcp-server-docker` 0.3.0 was also driven through the gate: `list_containers` returned data, and `stop_container` came back `403` with the target still running.
