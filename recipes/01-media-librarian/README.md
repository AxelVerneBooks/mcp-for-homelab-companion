# Recipe 01 — Read-Only Media Librarian

**Status:** ✅ Works OOTB · **Book ref:** Chapter 4 (filesystem), Recipe 1

The reference filesystem MCP server, pointed at a media tree, mounted **read-only**, with **no network**. The canonical "hello hands" of MCP.

## Run

```bash
cp .env.example .env      # optional: point MEDIA_DIR at your real tree
docker compose run --rm mount-check   # validates the mount (read-only)
docker compose config -q             # validates the file itself
```

## Stanza (stdio — no port, no HTTP; book, Chapter 3)

```json
{ "mcpServers": { "media-librarian": {
    "command": "docker",
    "args": ["run", "--rm", "-i",
             "--network", "none",
             "--user", "65534:65534", "--read-only", "--tmpfs", "/tmp",
             "--cap-drop", "ALL", "--security-opt", "no-new-privileges:true",
             "--memory", "256m", "--cpus", "0.5", "--pids-limit", "128",
             "-v", "${MEDIA_DIR:-/tank/media}:/media:ro",
             "mcp/filesystem:vX.Y.Z", "/media"] } } }
```

## First question

*"What's the largest file in my media folder and did anything land there this week?"*

## Scope notes (non-negotiables)

- `:ro` mount — the server physically cannot write.
- `network_mode: none` — nothing to phone home about, so it can't.
- Runs as `nobody` with a read-only rootfs, no capabilities, and memory/CPU/PID caps ([SECURITY.md](../../SECURITY.md)). If your media isn't world-readable, swap `65534:65534` for a read-only media user's UID:GID — never root.
- `MEDIA_DIR` must be a directory you'd hand a stranger with a clipboard; that's the threat model.
