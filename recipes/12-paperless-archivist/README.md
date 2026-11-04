# Recipe 12 — Paperless-ngx Archivist

**Status:** ⚠️ Needs backend (Paperless-ngx + token) · **Book ref:** companion-only recipe (not in the Chapter 10 appendix); follows the Chapter 5 scoping pattern

An MCP server over your Paperless-ngx archive. Paperless already OCRs, tags and dates every scan; MCP turns that into questions: *"when does the car insurance renew?"* without remembering which tag you used in 2022.

## Run

```bash
cp .env.example .env               # PAPERLESS_URL + dedicated user's token
docker compose run --rm preflight  # verify reachability + token before anything else
docker compose up -d
```

## Verify

`preflight` calls `GET $PAPERLESS_URL/api/documents/?page_size=1` with `Authorization: Token …` from inside a container and prints the `count` field — the number of documents this user can see. Expected output:

```
token OK, documents visible to this user: "count":1234
```

- `401` → wrong token, or the token belongs to a deleted user.
- `403` → the user exists but lacks the view permission for documents.
- `"count":0` on an archive you know is full → permissions, not a bug (see scope notes).

The same check by hand from the Docker host:

```bash
curl -s -H "Authorization: Token $PAPERLESS_TOKEN" "$PAPERLESS_URL/api/documents/?page_size=1"
```

## Stanza

```json
{ "mcpServers": { "paperless-archivist": {
    "url": "http://<docker-host>:9112/mcp" } } }
```

## First question

*"Find every invoice from the electricity provider this year and list the amounts and dates."*

## Scope notes

- **Dedicated user, view permissions only.** In Paperless-ngx, give the user only the *view* permissions under Settings → Users & Groups — no change, add or delete. Then log in as that user and generate the token from **My Profile → API Auth Token**. Never use the superuser's token.
- Paperless enforces per-document ownership: the dedicated user sees documents with no owner plus anything owned by or shared with it. If `count` is lower than expected, fix the sharing — don't promote the user to superuser.
- Bulk edit, delete and re-tag stay out of reach for good. A wrong tag across a few hundred documents is a weekend lost; a delete across them is worse (book, Ch. 5 — "reads forever" tier).
