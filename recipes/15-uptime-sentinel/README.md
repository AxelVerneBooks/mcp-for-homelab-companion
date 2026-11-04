# Recipe 15 — Uptime Kuma Sentinel

**Status:** ⚠️ Needs backend (Uptime Kuma + API key) · **Book ref:** companion-only recipe (not in the Chapter 10 appendix); follows the Chapter 5 scoping pattern

An MCP server over Uptime Kuma. Kuma already knows what's up, what's down and, for HTTPS monitors, when the certificate expires; MCP turns that into the morning question — *"anything I should know about?"* — and pairs naturally with recipe 02 (what's down → why did the container die).

## Run

```bash
cp .env.example .env               # KUMA_URL + API key
docker compose run --rm preflight  # verify reachability + key before anything else
docker compose up -d
```

## Verify

`preflight` calls `GET $KUMA_URL/metrics` from inside a container, authenticating with HTTP basic auth — empty username, API key as the password, which is how Uptime Kuma API keys are used — and counts the `monitor_status` series it gets back. Expected output:

```
key OK, monitors reporting status: 12
```

- `401` → wrong, expired or deactivated key.
- `0` monitors → the key works, but Uptime Kuma has nothing to report yet; add a monitor and re-run.
- Paused monitors can still appear in `/metrics` with their last recorded status. If a "1" looks too good to be true, check the monitor isn't paused in the UI.

The same check by hand (`grep` keeps the output to one line per monitor):

```bash
curl -s -u ":$KUMA_API_KEY" "$KUMA_URL/metrics" | grep '^monitor_status{'
```

## Stanza

```json
{ "mcpServers": { "uptime-sentinel": {
    "url": "http://<docker-host>:9115/mcp" } } }
```

## First question

*"Which monitors are down or slow right now, and which certificates expire in the next 30 days?"*

## Scope notes

- **API key over account password.** Uptime Kuma has a single admin account and no roles. API keys only unlock `/metrics` — read-only by construction, and revocable from Settings → API Keys without touching the admin login. Prefer a server that works from the key.
- Some Uptime Kuma MCP servers drive the web UI's Socket.IO API with the admin username and password instead. That credential can add, pause and delete monitors and change notifications — treat it like the Docker socket in recipe 02: deliberate, documented, and never the default.
- Set an expiry date on the key when you create it; a monitoring credential that outlives the experiment is a credential nobody remembers to revoke.
