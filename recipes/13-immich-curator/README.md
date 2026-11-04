# Recipe 13 — Immich Curator

**Status:** ⚠️ Needs backend (Immich + API key) · **Book ref:** companion-only recipe (not in the Chapter 10 appendix); follows the Chapter 5 scoping pattern

An MCP server over your Immich photo library. Immich already indexes dates, places, people and albums; MCP lets you ask across all of it — *"which trips from last year never got an album?"* — instead of scrolling the timeline.

## Run

```bash
cp .env.example .env               # IMMICH_URL + dedicated user's API key
docker compose run --rm preflight  # verify reachability + key before anything else
docker compose up -d
```

## Verify

`preflight` makes two calls from inside a container:

1. `GET $IMMICH_URL/api/server/ping` — no auth; a healthy server answers `{"res":"pong"}`.
2. `GET $IMMICH_URL/api/users/me` with the `x-api-key` header — proves the key works and prints the email of the user it acts as. If that user is an admin, preflight prints a warning.

Expected output:

```
reachable: {"res":"pong"}
key OK, acting as: "email":"mcp-bot@home.lan"
```

A `401` on step 2 means a wrong or deleted key. A `403` with `Missing required permission: user.read` means the key was created with scoped permissions that leave out `user.read` — add it. Note `IMMICH_URL` is the server root (default port `2283`), **without** a trailing `/api`. The same checks by hand:

```bash
curl -s "$IMMICH_URL/api/server/ping"
curl -s -H "x-api-key: $IMMICH_API_KEY" "$IMMICH_URL/api/users/me"
```

## Stanza

```json
{ "mcpServers": { "immich-curator": {
    "url": "http://<docker-host>:9113/mcp" } } }
```

## First question

*"Which months last year have the most photos, and which of those have no album yet?"*

## Scope notes

- **Dedicated non-admin user.** An Immich API key acts as the user who created it — make the key on a dedicated user, never on the admin account (preflight warns if you did).
- If your Immich release lets you choose permissions when creating a key, select only `*.read` permissions — at minimum `user.read` (preflight needs it), plus e.g. `asset.read` and `album.read` for whatever your MCP server reads. If it doesn't offer permissions, the user account is the scope — keep it non-admin.
- The library is the scope too: the key sees that user's assets and albums shared with that user. Share the albums you want the assistant to read; the rest stays invisible.
- Deleting or archiving assets is never promoted. Family photos are the one dataset in the homelab with no re-download button.
