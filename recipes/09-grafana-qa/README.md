# Recipe 09 — Grafana Question Answerer

**Status:** ⚠️ Needs backend (Grafana + viewer token) · **Book ref:** Chapter 5 (Recipe 9)

📖 **Read the chapter:** [_MCP for the Homelab_, Chapter 5](https://axelverne.com): the metrics reader and the Viewer-role default; Chapter 8 covers dashboards as the archive. All ten recipes are also in the Recipe Appendix (Chapter 10).

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
