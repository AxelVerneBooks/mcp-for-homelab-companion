# Recipe 11 — Forge Clerk (Gitea / Forgejo)

**Status:** ⚠️ Needs backend (Gitea or Forgejo + token) · **Book ref:** companion-only recipe (not in the Chapter 10 appendix); follows the Chapter 5 scoping pattern

An MCP server for your self-hosted forge. Gitea and Forgejo share the same `/api/v1` REST API, so one recipe covers both. The win is triage across every repo at once: stale PRs, forgotten issues, who's blocking whom — the homelab-configs repo you only remember exists when something breaks.

## Run

```bash
cp .env.example .env               # FORGE_URL + read-scoped token
docker compose run --rm preflight  # verify reachability + token before anything else
docker compose up -d
```

## Verify

`preflight` makes two calls from inside a container (so it tests the same network path the server will use):

1. `GET $FORGE_URL/api/v1/version` — no auth; proves the URL is right and reachable.
2. `GET $FORGE_URL/api/v1/user` with `Authorization: token …` — proves the token is valid and prints which login it acts as.

Expected output looks like:

```
reachable: {"version":"…"}
token OK, acting as: "login":"mcp-bot"
```

A `401` on step 2 means a wrong or revoked token; a `403` usually means the token lacks the `user` read scope. You can run the same two checks by hand from the Docker host:

```bash
curl -s "$FORGE_URL/api/v1/version"
curl -s -H "Authorization: token $FORGE_TOKEN" "$FORGE_URL/api/v1/user"
```

## Stanza

```json
{ "mcpServers": { "forge-clerk": {
    "url": "http://<docker-host>:9111/mcp" } } }
```

## First question

*"Which repos have pull requests open for more than two weeks, and what's each one waiting on?"*

## Scope notes

- **Dedicated user, read scopes only.** Gitea/Forgejo tokens are scoped per category (repository, issue, user, organization, …) with read/write levels — pick **read** for repository, issue and user, and no access for everything else, admin especially.
- The token sees exactly what its user sees. Add the dedicated user as a read-only collaborator (or to a read-only team) on the repos you want covered; private repos it can't read stay invisible — that's the design.
- Promoting to write (commenting, closing issues, merging) is the Chapter 5 ceremony: new token, new menu-notes entry, never an edit to the old one.
