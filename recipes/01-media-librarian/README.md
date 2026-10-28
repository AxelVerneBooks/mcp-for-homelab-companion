# Recipe 01 — Read-Only Media Librarian

**Status:** ✅ Works OOTB · **Book ref:** Chapter 4 (filesystem), Recipe 1

📖 **Read the chapter:** [_MCP for the Homelab_, Chapter 4](https://axelverne.com): how filesystem servers work, and why read-only and no network are the defaults. All ten recipes are also in the Recipe Appendix (Chapter 10).

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
             "-v", "${MEDIA_DIR:-/tank/media}:/media:ro",
             "mcp/filesystem:vX.Y.Z", "/media"] } } }
```

## First question

*"What's the largest file in my media folder and did anything land there this week?"*

## Scope notes (non-negotiables)

- `:ro` mount — the server physically cannot write.
- `network_mode: none` — nothing to phone home about, so it can't.
- `MEDIA_DIR` must be a directory you'd hand a stranger with a clipboard; that's the threat model.
