# Recipe 02 — Docker Forensics

**Status:** ✅ Works OOTB (socket is local) · **Book ref:** Chapter 4 (Docker), Recipe 2

📖 **Read the chapter:** [_MCP for the Homelab_, Chapter 4](https://axelverne.com): the Docker server and allowlist scoping; Chapter 7 (Rule 3) covers why the socket is root with a different hat. All ten recipes are also in the Recipe Appendix (Chapter 10).

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
