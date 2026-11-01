# Recipe 01 — Read-Only Media Librarian

**Status:** ✅ Works OOTB · **Book ref:** Chapter 4 (filesystem), Recipe 1

## Overview

The reference filesystem MCP server, pointed at a media tree, mounted **read-only**, with **no network**. The canonical "hello hands" of MCP.

This is a **stdio** server: it has no port and is not reachable over HTTP. Your client spawns it as a subprocess; `docker compose` here only *validates* the setup (image pull, volume mount, command shape).

## Requirements

- Docker with Compose.
- Image `mcp/filesystem:vX.Y.Z` — placeholder tag; pin the current release of the reference filesystem server.
- Optional: `MEDIA_DIR` in `.env` pointing at a real directory on the Docker host. Leave it unset to use the baked-in demo tree (`./demo-media`).

## Quick start

```bash
cp .env.example .env      # optional: point MEDIA_DIR at your real tree
docker compose run --rm mount-check   # validates the mount (read-only)
docker compose config -q             # validates the file itself
```

For real use, set `MEDIA_DIR` in `.env`, then swap the demo volume line in `docker-compose.yml` for the commented `${MEDIA_DIR}:/media:ro` line.

## Stanza (stdio — no port, no HTTP; book, Chapter 3)

```json
{ "mcpServers": { "media-librarian": {
    "command": "docker",
    "args": ["run", "--rm", "-i",
             "--network", "none",
             "-v", "${MEDIA_DIR:-/tank/media}:/media:ro",
             "mcp/filesystem:vX.Y.Z", "/media"] } } }
```

## First question

*"What's the largest file in my media folder and did anything land there this week?"*

## Scope notes (non-negotiables)

- `:ro` mount — the server physically cannot write.
- `network_mode: none` — nothing to phone home about, so it can't.
- `MEDIA_DIR` must be a directory you'd hand a stranger with a clipboard; that's the threat model.

## Troubleshooting

- **Nothing listens on a port / `curl` gets no answer** — expected. This is a stdio server; wire it with the `command` stanza above, not a `url`.
- **`mount-check` fails** — the demo tree `./demo-media` isn't readable from the container. Run it from this folder, and check the output it prints (it lists the top of `/media`).
- **Your real files don't show up** — the compose file mounts the demo tree by default; swap in the `${MEDIA_DIR}` volume line after setting `MEDIA_DIR`.
- **`vX.Y.Z` image not found** — the tag is a placeholder; pin a real release.

## License

MIT — see the [root LICENSE](../../LICENSE). Copyright (c) 2026 Axel Verne. Part of the free companion to [_MCP for the Homelab_](https://axelverne.com).
