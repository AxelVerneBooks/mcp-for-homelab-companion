# Recipe 09 — Grafana Question Answerer

**Status:** ⚠️ Needs backend (Grafana + viewer token) · **Transport:** streamable HTTP · **Book ref:** Chapter 5 (Recipe 9)

[mcp-grafana](https://github.com/grafana/mcp-grafana), Grafana Labs' official MCP server. It lets the assistant read dashboards and query datasources, and answer *"what does the last hour of CPU look like, and does it correlate with anything else on that dashboard?"* The correlation question is where it shines.

| | |
|---|---|
| Image | `grafana/mcp-grafana:2.1.1` |
| Needs | Grafana 9+ and a service-account token with the **Viewer** role |
| Endpoint | `http://<docker-host>:9109/mcp` with `Authorization: Bearer <GRAFANA_MCP_TOKEN>` |
| Writes | Off: `--disable-write` removes them, and the Viewer role couldn't use them anyway |

## Setup

1. **In Grafana:** Administration → Users and access → **Service accounts** → *Add service account* (`mcp`, role **Viewer**) → *Add service account token*. Copy the `glsa_…` token.
2. **Configure and start:**

   ```bash
   cd recipes/09-grafana-qa
   cp .env.example .env
   $EDITOR .env      # GRAFANA_URL, GRAFANA_TOKEN, GRAFANA_MCP_TOKEN=$(openssl rand -hex 32), MCP_HOSTNAME
   docker compose config -q
   docker compose up -d
   docker compose logs grafana-mcp    # expect: "Starting Grafana MCP server using StreamableHTTP transport"
   ```

3. **Prove the endpoint answers:**

   ```bash
   curl -s http://localhost:9109/mcp -X POST -H 'Authorization: Bearer <GRAFANA_MCP_TOKEN>' \
     -H 'Content-Type: application/json' -H 'Accept: application/json, text/event-stream' \
     -d '{"jsonrpc":"2.0","id":1,"method":"initialize","params":{"protocolVersion":"2025-11-25","capabilities":{},"clientInfo":{"name":"curl","version":"0"}}}'
   ```

   Expected: `"serverInfo"`. A `401` means a wrong token. A `403` means the host name in your URL isn't covered by `MCP_HOSTNAME`.

4. Add the stanza, restart your client, ask the first question.

## Stanza

```json
{ "mcpServers": { "grafana-qa": {
    "url": "http://<MCP_HOSTNAME>:9109/mcp",
    "headers": { "Authorization": "Bearer <GRAFANA_MCP_TOKEN>" } } } }
```

## First question

*"What does the last hour of CPU look like on the hypervisor, and does it correlate with anything else on that dashboard?"*

## Scope notes

- **Viewer role only.** It can read every dashboard and run read queries, but can't save, delete or alert-edit anything. `--disable-write` hides the write tools from the menu too, so the assistant doesn't waste turns on them.
- **Two different tokens:** `GRAFANA_TOKEN` is how the server talks to Grafana. `GRAFANA_MCP_TOKEN` is how your client talks to the server. Never reuse one as the other.
- **Raw-SQL datasources:** with `--disable-write`, the SQL passthrough tools are also removed (they can mutate data if the datasource user allows it). Keep it that way unless the datasource credentials themselves are read-only.
- Anonymous usage reporting to Grafana Labs is turned off (`GRAFANA_USAGE_STATS=disabled`).
- This is the recipe that multiplies the value of every other one: metrics + tool state = the assistant noticing what you'd miss. Keep dashboards for graphs and MCP for questions (book, Ch. 8: the dashboards become the archive, not the interface).

## Tested

During this audit the exact compose file ran against a real `grafana/grafana:13.0.11` with a Viewer service account. `user_info` and `search_dashboards` returned live data, a request without the bearer token got `401`, and a request with a Host header outside the allowlist got `403`.
