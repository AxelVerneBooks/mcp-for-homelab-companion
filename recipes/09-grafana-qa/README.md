# Recipe 09 — Grafana Question Answerer

**Status:** ⚠️ Needs backend (Grafana + viewer token) · **Book ref:** Chapter 5 (Recipe 9)

The Grafana MCP server — lets the assistant read dashboards and answer *"what does the last hour of CPU look like, and does it correlate with anything else on that dashboard?"* The correlation question is where it shines.

## Run

```bash
cp .env.example .env      # GRAFANA_URL + Viewer-role service account token
docker compose up -d
```

## Stanza

```json
{ "mcpServers": { "grafana-qa": {
    "url": "http://<docker-host>:9109/mcp" } } }
```

## First question

*"What does the last hour of CPU look like on the hypervisor, and does it correlate with anything else on that dashboard?"*

## Scope notes

- **Viewer role only** — create a service account (Administration → Users → Service accounts) and a token for it; the Viewer role can read every dashboard but touch nothing.
- This is the recipe that multiplies the value of every other one: metrics + tool state = the assistant noticing what you'd miss.
- Keep dashboards for graphs; keep MCP for questions. (Book, Ch. 8: the dashboards become the archive, not the interface.)

---

From the free, MIT-licensed companion repo for [_MCP for the Homelab_](https://axelverne.com) by Axel Verne. The book covers this recipe in Chapter 5, Recipe 9. Back to the [recipe catalog](https://axelvernebooks.github.io/mcp-for-homelab-companion/).
