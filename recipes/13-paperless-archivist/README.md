# Recipe 13 — Paperless-ngx Archivist

**Status:** ⚠️ Needs backend (Paperless-ngx + view-only token) · **Book ref:** Chapter 5 pattern (scope at the source), beyond the appendix

The Paperless-ngx MCP server — full-text search, tags, correspondents, and custom fields over every document you've ever scanned. The first question everyone asks: *"when does the car insurance renew, and what did we pay last year?"*

**Image:** `ghcr.io/cubinet-code/paperless-ngx-mcp:3.2.1` (pinned; targets Paperless-ngx 3.x; streamable HTTP on `/mcp`). On Paperless 2.x, pin `3.1.1` instead — the server's major version tracks the Paperless major it supports.

## Run

```bash
cp .env.example .env      # PAPERLESS_URL + token of a view-only user
docker compose up -d
```

## Verify

```bash
docker compose ps                     # paperless-mcp: running, not restarting
source .env && curl -sf -H "Authorization: Token $PAPERLESS_API_KEY" \
  "$PAPERLESS_URL/api/documents/?page_size=1" | head -c 200; echo   # token works at the source
curl -s http://127.0.0.1:9113/mcp -X POST \
  -H 'Content-Type: application/json' -H 'Accept: application/json, text/event-stream' \
  -d '{"jsonrpc":"2.0","id":1,"method":"initialize","params":{"protocolVersion":"2026-07-28","capabilities":{},"clientInfo":{"name":"curl","version":"0"}}}'
```

Expect a body containing `"serverInfo"`. Scope check: with the same token, `curl -X PATCH` a document's title — Paperless must answer **403**. If it succeeds, the user isn't view-only; fix that before wiring the stanza.

## Stanza

Client on the Docker host, or via `ssh -L 9113:127.0.0.1:9113 <docker-host>`:

```json
{ "mcpServers": { "paperless-archivist": {
    "url": "http://127.0.0.1:9113/mcp" } } }
```

## First question

*"Find every insurance document from the last two years and tell me which policies renew in the next 60 days."*

## Scope notes

- **Dedicated user with view-only permissions** (Admin → Users & Groups → Permissions: *View* on documents, tags, correspondents, document types). The server exposes edit, delete, trash, and share-link tools — Paperless's own permission check is what makes them inert. Scope at the source, not at the menu (book, Ch. 5).
- Share links are the sneaky one: a tool that mints a public URL to a tax return is an exfiltration path. Keep the user unable to create them, even after you promote tagging writes.
- No built-in auth on the HTTP endpoint → `127.0.0.1` binding in compose. Don't widen it.
- Your documents are the most personal data in the homelab. Decide *before* wiring this which model provider sees OCR text, and say it out loud in your menu-notes file.
