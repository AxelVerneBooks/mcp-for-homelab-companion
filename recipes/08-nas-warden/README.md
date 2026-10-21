# Recipe 08 — NAS Health Warden

**Status:** ⚠️ Needs backend (TrueNAS SCALE + API key) · **Transport:** streamable HTTP over TLS · **Book ref:** Chapter 5 (infrastructure hands), Recipe 8

[truenas-mcp](https://github.com/cedricziel/truenas-mcp), a Go MCP server for the TrueNAS SCALE JSON-RPC API: pool health, disk temps, dataset usage. Read-only, full stop.

| | |
|---|---|
| Image | `ghcr.io/cedricziel/truenas-mcp:0.4.2` |
| Needs | TrueNAS SCALE **25.04+** and an API key for a dedicated, read-only user |
| Endpoint | `https://<docker-host>:9108/mcp`. Your client sends the TrueNAS API key as `Authorization: Bearer …` |
| Writes | Off (`TRUENAS_MCP_ENABLE_WRITES` is deliberately unset) |

## Setup

1. **In TrueNAS:** Credentials → Users → *Add* a dedicated user (e.g. `mcp-warden`) with a **read-only** role (e.g. *Read-only Administrator*). On that user: *API Keys → Add*. Copy the key.
2. **Make a TLS certificate for the MCP listener** (the API key travels on this hop, so it gets TLS):

   ```bash
   cd recipes/08-nas-warden
   mkdir -p certs
   openssl req -x509 -newkey rsa:2048 -nodes -days 825 \
     -subj "/CN=docker-host.local" \
     -addext "subjectAltName=DNS:docker-host.local,DNS:localhost,IP:127.0.0.1" \
     -keyout certs/tls.key -out certs/tls.crt
   sudo chown 65532:65532 certs/tls.key     # the image runs as distroless "nonroot"
   ```

   Replace `docker-host.local` with the name your client will use. Then add `certs/tls.crt` to your client machine's trust store, or use a cert from your own CA. `certs/` is gitignored.

3. **Configure and start:**

   ```bash
   cp .env.example .env
   $EDITOR .env        # TN_HOST (host or host:port, no scheme), TN_INSECURE
   docker compose config -q
   docker compose up -d
   docker compose logs truenas-mcp     # expect: tls=on writes=disabled
   ```

4. **Prove the endpoint answers** (with your TrueNAS API key):

   ```bash
   curl -s --cacert certs/tls.crt https://localhost:9108/mcp -X POST -H 'Authorization: Bearer <TRUENAS_API_KEY>' \
     -H 'Content-Type: application/json' -H 'Accept: application/json, text/event-stream' \
     -d '{"jsonrpc":"2.0","id":1,"method":"initialize","params":{"protocolVersion":"2025-11-25","capabilities":{},"clientInfo":{"name":"curl","version":"0"}}}'
   ```

   Expected: `"serverInfo":{"name":"truenas-mcp"...}`. Without the header you get `401`.

5. Add the stanza, restart your client, ask the first question.

## Stanza

```json
{ "mcpServers": { "nas-warden": {
    "url": "https://docker-host.local:9108/mcp",
    "headers": { "Authorization": "Bearer <TRUENAS_API_KEY>" } } } }
```

## First question

*"How is the pool, and is any disk running hotter than its siblings?"*

## Scope notes

- **Read-only, twice.** The user's role can't change anything, and the server ships with writes disabled. Storage servers are where a fat-fingered "cleanup" tool earns a chapter in a different book (book, Ch. 5).
- **The key lives in your client, not on the Docker host.** The container holds no TrueNAS credential at all, and each client authenticates as itself.
- **Why TLS on the MCP hop:** the server warns that API keys sent in the clear may be revoked by TrueNAS. `TRUENAS_MCP_ALLOW_PLAINTEXT=true` exists, but use it only if the listener is bound to loopback (`"127.0.0.1:9108:8443"`) and the client runs on the same host.
- **Older SCALE / CORE:** this server uses the JSON-RPC WebSocket API of SCALE 25.04+. The legacy `/websocket` endpoint and the REST API are being removed upstream, which is why the earlier `wss://…/websocket` setting is gone.
- **No container healthcheck:** upstream's `--healthcheck` probe reports `400` when TLS is on (v0.4.2). Use `docker compose logs` instead.

## Tested

During this audit, truenas-mcp v0.4.2 (built from the tagged source) was started with these settings and a self-signed cert. It answered `initialize` over TLS, returned `401` without a bearer token, and logged `writes=disabled`. A live TrueNAS was not available, so tool calls against a real pool are untested here.
