# Recipe 06 — Radarr Butler (the *arr pattern)

**Status:** ⚠️ Needs backend (Radarr + API key) · **Book ref:** Chapter 5 (library hands), Recipe 6

📖 **Read the chapter:** [_MCP for the Homelab_, Chapter 5](https://axelverne.com): library hands and the one-server-per-*arr-app pattern. All ten recipes are also in the Recipe Appendix (Chapter 10).

Radarr via MCP — and the **pattern for the whole *arr family**: Sonarr, Prowlarr, Lidarr are the same compose file with a different image, port, and API key.

## Run

```bash
cp .env.example .env      # ARR_URL + API key (Settings → General → Security)
docker compose up -d
```

## Stanza

```json
{ "mcpServers": { "radarr-butler": {
    "url": "http://<docker-host>:9106/mcp" } } }
```

## First question

*"What's sitting in Radarr's queue, and what's been stuck longest?"*

## Scope notes

- **Read-only until the couch-grab day** — promoting "find and grab the 4K remake" write access is the Chapter 5 ceremony, complete with a menu-notes entry.
- One server per *arr app; never share one server across apps via multiple keys — the menu gets muddy and the audit gets impossible.
- API keys are per-app: Settings → General → Security in each app's UI.
