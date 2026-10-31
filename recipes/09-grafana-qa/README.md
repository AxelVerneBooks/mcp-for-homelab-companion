# Recipe 09 — Grafana Question Answerer

**Status:** ⚠️ Needs backend (Grafana + viewer token) · **Book ref:** Chapter 5 (Recipe 9)

Grafana's own MCP server ([`grafana/mcp-grafana`](https://github.com/grafana/mcp-grafana), pinned to `2.1.1`) — lets the assistant read dashboards and answer *"what does the last hour of CPU look like, and does it correlate with anything else on that dashboard?"* The correlation question is where it shines.

## Run

```bash
cp .env.example .env      # GRAFANA_URL + Viewer-role token + MCP_ALLOWED_HOSTS
docker compose up -d --wait
curl -sf http://localhost:9109/healthz && echo healthy
```

`MCP_ALLOWED_HOSTS` is the server's Host-header allowlist (DNS-rebinding protection). It defaults to `localhost:9109,127.0.0.1:9109`; add the `host:port` your client actually dials (e.g. `nas.lan:9109`) or connections from other machines get rejected.

## Stanza

```json
{ "mcpServers": { "grafana-qa": {
    "url": "http://<docker-host>:9109/mcp" } } }
```

## First question

*"What does the last hour of CPU look like on the hypervisor, and does it correlate with anything else on that dashboard?"*

## Scope notes

- **Viewer role only** — the compose file also passes `--disable-write`, so write tools aren't even registered. Create a service account (Administration → Users → Service accounts) and a token for it; the Viewer role can read every dashboard but touch nothing.
- This is the recipe that multiplies the value of every other one: metrics + tool state = the assistant noticing what you'd miss.
- Keep dashboards for graphs; keep MCP for questions. (Book, Ch. 8: the dashboards become the archive, not the interface.)
