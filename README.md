# MCP for the Homelab — Companion Repo

![License: MIT](https://img.shields.io/badge/license-MIT-green) ![Smoke test](https://img.shields.io/badge/smoke%20test-22%20passed%20·%200%20failed-brightgreen) ![Book](https://img.shields.io/badge/book-%248.99%20flat%20·%20DRM%20free-2ea44f)

**This is the free, MIT-licensed companion to [_MCP for the Homelab_](https://axelverne.com)** — the ebook that teaches the why, the scoping ritual, the security model, and the error catalog behind these recipes. The recipes stand alone; the book makes you dangerous.

One folder per recipe from the Recipe Appendix (Chapter 10 of the book), plus recipes 11–15 that extend the same patterns to more of the homelab. Each folder is self-contained: `cp` the env example, edit it, `docker compose up -d`, wire the stanza, ask the first question.

## Repo map

```
recipes/
  01-media-librarian/      filesystem MCP server, read-only   → stdio · works OOTB (demo tree)
  02-docker-forensics/     docker-mcp with allowlist          → stdio · socket/env check OOTB
  03-ha-concierge/         Home Assistant MCP                 → HTTP · needs HA + token
  04-proxmox-auditor/      Proxmox MCP                        → HTTP · needs PVE + API token
  05-qbittorrent-manager/  qBittorrent MCP                    → HTTP · needs qBit + account
  06-arr-butler/           Radarr MCP (pattern for all *arr)  → HTTP · needs Radarr + API key
  07-pihole-detective/     Pi-hole MCP                        → HTTP · needs Pi-hole + token
  08-nas-warden/           TrueNAS MCP                        → HTTP · needs TrueNAS + key
  09-grafana-qa/           Grafana MCP                        → HTTP · needs Grafana + viewer token
  10-custom-front-desk/    full working example server        → HTTP · works OOTB (mock backend)
  11-jellyfin-curator/     Jellyfin MCP (bearer-token gated)  → HTTP · needs Jellyfin + API key
  12-kuma-sentinel/        Uptime Kuma 2.x MCP                → HTTP · needs Kuma + login (localhost-bound)
  13-paperless-archivist/  Paperless-ngx MCP                  → HTTP · needs Paperless + view-only token (localhost-bound)
  14-gitea-scribe/         official Gitea MCP, read-only      → HTTP · needs Gitea + read-scoped token
  15-prometheus-analyst/   Prometheus MCP (PromQL)            → HTTP · needs Prometheus
tools/smoke.sh            validates all 15 configs + pinned tags (11–15); live-tests 01 (mount) + 10 (handshake)
```

**Transport note:** the shelf servers you spawn *from your client* (01, 02) are stdio — no ports, no HTTP. Recipes 03–15 serve streamable HTTP from your compose stack. Every recipe's README shows the correct stanza shape for its transport (book, Chapter 3).

## The 5-minute path (zero external services)

```bash
./tools/smoke.sh
```

The smoke script runs two tiers: **Tier 1** validates every recipe's compose file (syntax + env shape) and checks that recipes 11–15 resolve to pinned release tags, so a typo anywhere in the repo announces itself; **Tier 2** live-tests the two self-contained recipes — recipe 01's read-only mount against the baked-in demo tree, and recipe 10's *actual MCP handshake* over HTTP against its mock backend. If smoke passes, your Docker setup and the repo's config patterns are sound; everything else is the same pattern pointed at different APIs.

## The general ritual (every recipe, every time)

1. `cd recipes/0X-name && cp .env.example .env && $EDITOR .env`
2. Run the recipe's validation command from its README (stdio recipes: `docker compose run --rm ...`; HTTP recipes: `docker compose up -d --build`).
3. Add the stanza from the recipe's README to your MCP client config — note whether it's a `command` (stdio) or `url` (HTTP) stanza.
4. Restart the client, ask the recipe's first question.
5. When it works, *then* consider promoting read-only scope — never before. (Book, Chapter 7.)

## README legend used in every recipe folder

- **Works OOTB** — no backend needed; safe to `up` right now.
- **Needs backend** — requires the real service running and credentials; the compose file still validates and the container will start-and-error until you fill `.env` (that's the designed failure mode: loud, early, honest).
- **Stanza** — the exact JSON block for your client's `mcpServers`.

## Safety defaults, enforced by the files themselves

- Every optional-write server ships **reads only**; write tools are commented in source with the promotion checklist in the recipe README (book: Chapter 5/6).
- Filesystem mounts are `:ro`; network-exiled where possible (`network_mode: none` or isolated compose networks).
- Secrets only ever come from `.env` files (gitignored); the examples contain no credentials, only placeholders.
- The Docker socket recipe mounts it **only** for recipe 02, with `ALLOW_LIST` set — treat any other recipe demanding the socket as a bug (report it, don't run it).

## Versioning rule

Recipes 01–10 (the book's appendix) use placeholder tags of the form `vX.Y.Z`. Before cooking one, pin the current release of the referenced server (the book's Chapter 5 explains why pinning is the difference between a stack and a surprise). `grep -r "vX.Y.Z" recipes/` lists everything you must pin.

Recipes 11–15 ship **already pinned** to a specific upstream release (look for `# PINNED` in the compose file; the smoke test fails if one drifts to `latest`). Bump those tags deliberately: read the upstream release notes, re-check env names against its README, re-run the recipe's *Verify* block.

| Recipe | Pinned image |
|---|---|
| 11 Jellyfin Curator | `ghcr.io/jaredtrent/jellyfin-mcp:2026.604.2` |
| 12 Kuma Sentinel | `davidfuchs/mcp-uptime-kuma:0.12.1` |
| 13 Paperless Archivist | `ghcr.io/cubinet-code/paperless-ngx-mcp:3.2.1` |
| 14 Gitea Scribe | `docker.gitea.com/gitea-mcp-server:1.6.0` |
| 15 Prometheus Analyst | `ghcr.io/pab1it0/prometheus-mcp-server:1.6.2` |
