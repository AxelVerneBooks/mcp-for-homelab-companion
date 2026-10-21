# Recipe 01 — Read-Only Media Librarian

**Status:** ✅ Works OOTB · **Transport:** stdio · **Book ref:** Chapter 4 (filesystem), Recipe 1

The reference filesystem MCP server ([`mcp/filesystem`](https://hub.docker.com/r/mcp/filesystem), from [modelcontextprotocol/servers](https://github.com/modelcontextprotocol/servers/tree/main/src/filesystem)), pointed at a media tree, mounted **read-only**, with **no network**. The canonical "hello hands" of MCP.

| | |
|---|---|
| Image | `mcp/filesystem:1.0.2` |
| Needs | Docker. Nothing else — a demo tree ships in `./demo-media`. |
| Writes | Impossible: `:ro` mount, so every write tool returns `EROFS`. |

## Setup

```bash
cd recipes/01-media-librarian
cp .env.example .env                  # optional: uncomment MEDIA_DIR=/your/media
docker compose config -q              # 1. the file is valid
docker compose run --rm mount-check   # 2. prints "mount OK (read-only)" and "write blocked OK"
```

3. **Talk to the server by hand** (optional, proves the image works before you touch a client):

   ```bash
   printf '%s\n' \
     '{"jsonrpc":"2.0","id":1,"method":"initialize","params":{"protocolVersion":"2025-11-25","capabilities":{},"clientInfo":{"name":"cli","version":"0"}}}' \
     '{"jsonrpc":"2.0","method":"notifications/initialized"}' \
     '{"jsonrpc":"2.0","id":2,"method":"tools/call","params":{"name":"list_directory","arguments":{"path":"/media"}}}' \
     | docker compose run --rm -T media-mcp
   ```

   Expected: an `initialize` result from `secure-filesystem-server`, then `[DIR] movies`.

4. Add the stanza below to your client, restart it, ask the first question.

## Stanza (stdio — no port, no HTTP; book, Chapter 3)

Replace `/tank/media` with the **absolute** path of your media tree (or of this folder's `demo-media`). MCP clients do not expand shell variables in `args`.

```json
{ "mcpServers": { "media-librarian": {
    "command": "docker",
    "args": ["run", "--rm", "-i",
             "--network", "none",
             "-v", "/tank/media:/media:ro",
             "mcp/filesystem:1.0.2", "/media"] } } }
```

## First question

*"What's the largest file in my media folder and did anything land there this week?"*

## Scope notes (non-negotiables)

- `:ro` mount, so the server physically cannot write. Its write tools still appear in the menu, but every call fails with `EROFS`. That failure is the proof the scope holds.
- `network_mode: none` / `--network none`: nothing to phone home about, so it can't.
- `MEDIA_DIR` must be a directory you'd hand a stranger with a clipboard; that's the threat model.

## Tested

`tools/smoke.sh` runs `mount-check` and a full stdio `initialize` → `list_directory` round trip against the demo tree, and confirms a `write_file` call is refused.
