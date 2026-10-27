# Recipe 02 — Docker Forensics

**Status:** ✅ Works OOTB (socket is local) · **Book ref:** Chapter 4 (Docker), Recipe 2

The docker-mcp server scoped with `ALLOW_LIST` — the assistant can see and manage *only* the containers you name. This is the recipe that turns "list my containers" into a one-sentence question.

## Run

```bash
cp .env.example .env      # set ALLOW_LIST to your container names
docker compose run --rm socket-check  # validates socket visibility + env shape
```

## Stanza (stdio)

```json
{ "mcpServers": { "docker-forensics": {
    "command": "docker",
    "args": ["run", "--rm", "-i",
             "--network", "none",
             "--read-only", "--tmpfs", "/tmp",
             "--cap-drop", "ALL", "--security-opt", "no-new-privileges:true",
             "--memory", "256m", "--cpus", "0.5", "--pids-limit", "128",
             "-v", "/var/run/docker.sock:/var/run/docker.sock",
             "--env-file", "<this folder>/.env",
             "docker-mcp:vX.Y.Z"] } } }
```

## First question

*"Which containers have restarted more than once this week, and why?"*

## Scope notes

- **The socket is root with a different hat** (book, Ch. 7 Rule 3). This is the *only* recipe in the repo that mounts it.
- `ALLOW_LIST` is the security boundary, not a suggestion. A container not in the list is invisible to the assistant — that's the design.
- Run this server on the host whose containers you're exposing; the socket path is host-local.
- `--network none`: the server talks to the Docker API over the mounted Unix socket, so it needs no network at all.
- **The documented root exception** ([SECURITY.md](../../SECURITY.md)): the socket is owned by `root:docker`, so the stanza doesn't force `--user`. To run unprivileged, add `"--user", "65534:<docker-gid>"` (find the GID with `getent group docker`) — but understand that any process that can open the socket can drive the Docker API, so `ALLOW_LIST` stays the real boundary either way. Mounting the socket `:ro` does **not** make the API read-only.
