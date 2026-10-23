# Recipe 14 — Gitea Scribe

**Status:** ⚠️ Needs backend (Gitea + read-only token) · **Book ref:** Chapter 5 pattern (two fences), beyond the appendix

The official Gitea MCP server — repos, issues, PRs, commits, and releases on your self-hosted forge. Your homelab config lives in git; this is the recipe that lets the assistant answer *"what changed in the compose repo the week the DNS broke?"*

**Image:** `docker.gitea.com/gitea-mcp-server:1.6.0` (pinned; also published as `gitea/gitea-mcp-server:1.6.0` on Docker Hub; HTTP on `:8080/mcp`, health on `/healthz`).

## Run

```bash
cp .env.example .env      # GITEA_HOST + read-only bot token
docker compose up -d
```

## Verify

```bash
docker compose ps                                     # gitea-mcp: running, not restarting
curl -sf http://localhost:9114/healthz && echo OK      # server is up
source .env && curl -sf -H "Authorization: token $GITEA_ACCESS_TOKEN" \
  "$GITEA_HOST/api/v1/user" | head -c 200; echo        # token resolves to the BOT user, not you
curl -s http://localhost:9114/mcp -X POST \
  -H 'Content-Type: application/json' -H 'Accept: application/json, text/event-stream' \
  -d '{"jsonrpc":"2.0","id":1,"method":"initialize","params":{"protocolVersion":"2026-07-28","capabilities":{},"clientInfo":{"name":"curl","version":"0"}}}'
```

Expect a body containing `"serverInfo"`. Then send `{"jsonrpc":"2.0","id":2,"method":"tools/list"}` (with the `Mcp-Session-Id` header from the initialize response) and confirm no `create_*`, `delete_*`, or `merge_*` tools are listed — that's `GITEA_READONLY` doing its job.

## Stanza

```json
{ "mcpServers": { "gitea-scribe": {
    "url": "http://<docker-host>:9114/mcp" } } }
```

## First question

*"What changed in the homelab-compose repo between the 1st and the 7th, and which commit touched DNS?"*

## Scope notes

- **Two fences:** the token's scopes (`read:repository`, `read:issue`, `read:user`) are the real boundary; `GITEA_READONLY=true` hides write tools so the model never even sees them. Either alone is weaker than both.
- **Dedicated bot user**, added as a *reader* collaborator only on the repos you want visible. Private repos it can't see are invisible to the assistant — that's the design.
- Never let a write-scoped token near a repo that holds secrets or deploy keys; a "helpful" commit to an IaC repo is a deploy.
- Forgejo works via the Gitea-compatible API; if a tool errors on Forgejo, it's the API drift, not your token.
- Env names track the pinned release; re-check them against the upstream README when you bump the tag.
