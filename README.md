# MCP for the Homelab — Companion Repo

![License: MIT](https://img.shields.io/badge/license-MIT-green) ![Smoke test](https://img.shields.io/badge/smoke%20test-12%20passed%20·%200%20failed-brightgreen) ![Book](https://img.shields.io/badge/book-%248.99%20flat%20·%20DRM%20free-2ea44f)

**This is the free, MIT-licensed companion to [_MCP for the Homelab_](https://axelverne.com)** — the ebook that teaches the why, the scoping ritual, the security model, and the error catalog behind these recipes. The recipes stand alone; the book makes you dangerous.

One folder per recipe from the Recipe Appendix (Chapter 10 of the book). Each folder is self-contained: `cp` the env example, edit it, `docker compose up -d`, wire the stanza, ask the first question.

## Recipe comparison

| # | Recipe | Use case | What it needs | Transport · port | Difficulty | Book chapter |
|---|--------|----------|---------------|------------------|------------|--------------|
| 01 | [Media Librarian](recipes/01-media-librarian/) | Ask questions about a media tree (sizes, new arrivals) | Nothing; demo tree included. Optional: a host directory, mounted `:ro` | stdio · none (`network_mode: none`) | 🟢 Easy | [Ch. 4](https://axelverne.com) |
| 02 | [Docker Forensics](recipes/02-docker-forensics/) | Restart loops, container health, logs for named containers | Local Docker socket, plus an `ALLOW_LIST` of container names | stdio · none | 🟢 Easy to run · ⚠️ socket is root-equivalent | [Ch. 4](https://axelverne.com) (+ Ch. 7 Rule 3) |
| 03 | [HA Concierge](recipes/03-ha-concierge/) | Run scenes and control lights/devices in plain language | Home Assistant, plus a long-lived token from a **dedicated** houseguest-scoped user | HTTP · 9103 | 🟡 Medium (user scoping) | [Ch. 5](https://axelverne.com) |
| 04 | [Proxmox Auditor](recipes/04-proxmox-auditor/) | Find idle VMs and audit RAM/resource use | Proxmox VE node, plus a PVEAuditor-role API token; TLS trust for self-signed certs | HTTP · 9104 | 🟡 Medium (token + TLS) | [Ch. 5](https://axelverne.com) |
| 05 | [qBittorrent Manager](recipes/05-qbittorrent-manager/) | Diagnose stalled downloads and queue problems | qBittorrent WebUI, a dedicated account, and qBit's existing Docker network (`external`) | HTTP · 9105 | 🟡 Medium (shared network) | [Ch. 5](https://axelverne.com) |
| 06 | [*arr Butler](recipes/06-arr-butler/) | Radarr queue and library questions (pattern for Sonarr/Prowlarr/Lidarr) | Radarr, plus its API key | HTTP · 9106 | 🟢 Easy | [Ch. 5](https://axelverne.com) |
| 07 | [Pi-hole Detective](recipes/07-pihole-detective/) | Blocked-query and per-client DNS investigation | Pi-hole (v6 auth model), plus a read-only token | HTTP · 9107 | 🟡 Medium (v6 auth / version pin) | [Ch. 5](https://axelverne.com) |
| 08 | [NAS Warden](recipes/08-nas-warden/) | Pool health, disk temps, dataset usage | TrueNAS SCALE, plus a read-only API key; websocket (`wss://`) reachability | HTTP · 9108 | 🟠 Medium–hard (websocket through proxies) | [Ch. 5](https://axelverne.com) |
| 09 | [Grafana Q&A](recipes/09-grafana-qa/) | Ask questions of dashboards and correlate metrics | Grafana, plus a Viewer-role service-account token | HTTP · 9109 | 🟢 Easy | [Ch. 5](https://axelverne.com) |
| 10 | [Custom Front Desk](recipes/10-custom-front-desk/) | Template for wrapping any API as your own MCP server | Nothing; mock backend included. Builds two `python:3.12-slim` images locally | HTTP · 9110 | 🟢 Easy to run · 🔴 Advanced to adapt | [Ch. 6](https://axelverne.com) |

**Footprint:** every recipe is a single MCP server container (recipe 10 adds one mock-API container, and 01/02 add a throwaway alpine check). None needs a GPU or persistent storage. Recipes 01 and 02 open no ports. Recipes 03–10 each claim one host port, listed above. All recipes are written up together in the Recipe Appendix (Chapter 10).

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
tools/smoke.sh            validates all 10 configs; live-tests 01 (mount) + 10 (handshake)
```

**Transport note:** the shelf servers you spawn *from your client* (01, 02) are stdio — no ports, no HTTP. Recipes 03–10 serve streamable HTTP from your compose stack. Every recipe's README shows the correct stanza shape for its transport (book, Chapter 3).

## The 5-minute path (zero external services)

```bash
./tools/smoke.sh
```

The smoke script runs two tiers: **Tier 1** validates every recipe's compose file (syntax + env shape), so a typo anywhere in the repo announces itself; **Tier 2** live-tests the two self-contained recipes — recipe 01's read-only mount against the baked-in demo tree, and recipe 10's *actual MCP handshake* over HTTP against its mock backend. If smoke passes, your Docker setup and the repo's config patterns are sound; everything else is the same pattern pointed at different APIs.

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

Every image tag in this repo is a placeholder of the form `vX.Y.Z`. Before cooking a recipe, pin the current release of the referenced server (the book's Chapter 5 explains why pinning is the difference between a stack and a surprise). `grep -r "vX.Y.Z" recipes/` lists everything you must pin.
