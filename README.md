# MCP for the Homelab — Companion Repo

[![Validate recipes](https://github.com/AxelVerneBooks/mcp-for-homelab-companion/actions/workflows/validate-recipes.yml/badge.svg)](https://github.com/AxelVerneBooks/mcp-for-homelab-companion/actions/workflows/validate-recipes.yml)
[![License: MIT](https://img.shields.io/badge/license-MIT-green)](LICENSE)
![Recipes](https://img.shields.io/badge/recipes-10-blue)
![Docker Compose](https://img.shields.io/badge/docker%20compose-v2-2496ED?logo=docker&logoColor=white)
![MCP](https://img.shields.io/badge/MCP-2025--11--25-8A2BE2)
![Images pinned](https://img.shields.io/badge/images-pinned-brightgreen)
[![Book: MCP for the Homelab](https://img.shields.io/badge/book-MCP%20for%20the%20Homelab-orange)](https://axelverne.com)

**Ten copy-paste Docker Compose recipes that give your AI assistant safe, scoped hands in your homelab**: Plex-style media trees, Docker, Home Assistant, Proxmox, qBittorrent, the *arr stack, Pi-hole, TrueNAS, Grafana, and any API you can wrap yourself.

> 📘 **This is the free companion to the book [_MCP for the Homelab_](https://axelverne.com) by Axel Verne.**
> The recipes stand alone. The book teaches the *why* behind them: the scoping ritual, the security model, the promotion ceremony, and the error catalog for when things go sideways. $8.99 flat, DRM-free, at **[axelverne.com](https://axelverne.com)**.

Every recipe here uses a **real, maintained MCP server**, **pinned to an exact release**, defaults to **read-only**, and is checked in CI on every push.

## Quickstart (5 minutes, zero external services)

```bash
git clone https://github.com/AxelVerneBooks/mcp-for-homelab-companion.git
cd mcp-for-homelab-companion
./tools/smoke.sh
```

You need Docker with Compose v2, `curl` and `jq`. The smoke test validates all ten recipes, then live-tests the three that need no backend:

- **01** completes an MCP stdio round trip, and a write is refused by the read-only mount.
- **02** confirms the Docker socket gate allows reads and refuses writes.
- **10** builds a custom server, completes the HTTP handshake, and makes a real tool call.

Green means your Docker setup is sound; everything else is the same pattern pointed at a different API.

**Then cook your first real recipe:**

```bash
cd recipes/01-media-librarian
cp .env.example .env              # point MEDIA_DIR at your media
docker compose run --rm mount-check
# paste the stanza from the recipe README into your MCP client, restart it, ask away
```

## The recipes

| # | Recipe | Gives your assistant | MCP server (pinned) | Transport · port | Status |
|---|---|---|---|---|---|
| 01 | [Media Librarian](recipes/01-media-librarian) | Read-only view of your media tree | `mcp/filesystem:1.0.2` | stdio | ✅ OOTB |
| 02 | [Docker Forensics](recipes/02-docker-forensics) | Container state, logs, stats (writes blocked) | `mcp-server-docker` 0.3.0 + `docker-socket-proxy:v0.5.0` | stdio | ✅ OOTB |
| 03 | [HA Concierge](recipes/03-ha-concierge) | Home Assistant states and history | `ha-mcp:8.7.0` | HTTP · 9103 | ⚠️ needs HA |
| 04 | [Proxmox Auditor](recipes/04-proxmox-auditor) | Nodes, VMs, storage, logs (auditor role) | `proxmoxmcp-plus:v0.6.6` | HTTP · 9104 | ⚠️ needs PVE |
| 05 | [qBittorrent Night Manager](recipes/05-qbittorrent-manager) | Queue diagnostics, stalled-torrent triage | `qbittorrent-mcp-rs:0.3.9` | SSE · 9105 | ⚠️ needs qBit |
| 06 | [Radarr Butler](recipes/06-arr-butler) | Queue, calendar, library (the *arr pattern) | `mcp-arr:1.7.3` | HTTP · 9106 | ⚠️ needs Radarr |
| 07 | [Pi-hole Detective](recipes/07-pihole-detective) | Query logs, top blocked clients (read-only) | `pihole-mcp:0.9.0` | HTTP · 9107 | ⚠️ needs Pi-hole v6 |
| 08 | [NAS Warden](recipes/08-nas-warden) | Pool health, disk temps, datasets (read-only) | `truenas-mcp:0.4.2` | HTTPS · 9108 | ⚠️ needs TrueNAS SCALE |
| 09 | [Grafana Q&A](recipes/09-grafana-qa) | Dashboards and metric queries (Viewer) | `grafana/mcp-grafana:2.1.1` | HTTP · 9109 | ⚠️ needs Grafana |
| 10 | [Custom Front Desk](recipes/10-custom-front-desk) | A full, readable MCP server you can fork | built locally (`mcp==1.30.0`) | HTTP · 9110 | ✅ OOTB |

✅ **OOTB** means it works out of the box, with no backend: safe to run right now. ⚠️ means it needs the real service and credentials. The compose file still validates, and the server tells you loudly what's missing.

## How every recipe works

1. `cd recipes/NN-name && cp .env.example .env && $EDITOR .env`
2. `docker compose config -q`, then the recipe's own check (`run --rm …-check` for stdio recipes, `up -d` + a `curl` handshake for HTTP ones).
3. Paste the recipe's **stanza** into your client's `mcpServers`. Note whether it's a `command` (stdio), `url` (streamable HTTP) or `"type": "sse"` stanza, and whether it needs an `Authorization` header.
4. Restart the client and ask the recipe's **first question**.
5. When it works, *then* consider promoting write scope, and never before (book, Chapter 7).

Each recipe README has the same sections: **Setup** (numbered, with expected output), **Stanza**, **First question**, **Scope notes** (what's locked, and how), and **Tested** (exactly what was verified, and what wasn't).

## Safety defaults, enforced by the files themselves

- **Read-only by default, enforced in the server or the backend, not in a prompt.** Read-only modes (03, 07), tool allowlists (04), `--disable-write` (09), writes-off defaults (08), an API gate that returns `403` (02), and `:ro` mounts (01). Where a server has no read-only switch (05, 06), the README says so plainly and lists the write tools to keep behind your client's approval prompt.
- **Every HTTP endpoint is authenticated**: a bearer token (04, 05, 07, 09), the caller's own API key (08), or a generated secret path (03). The *arr server has no auth of its own (06), so it binds to `127.0.0.1` by default. Recipe 10 serves only its mock backend: add auth before you aim it at anything real.
- **Secrets only come from `.env` files** (gitignored). The examples contain placeholders, never credentials. Required secrets fail `docker compose up` loudly if missing.
- **The Docker socket is mounted by exactly one service** in the whole repo (recipe 02's read-only proxy). Treat any other recipe demanding the socket as a bug.
- Filesystem mounts are `:ro`. Networks are isolated where possible (`network_mode: none`, `internal: true`, per-recipe networks).

## Versioning rule

Every image is pinned to an exact release (or digest), and CI fails on `latest`, a missing tag, or a placeholder (`tools/check-pins.sh`). Upgrading is a deliberate act: bump the tag, run `./tools/smoke.sh`, and read the upstream changelog. Chapter 5 of the book explains why pinning is the difference between a stack and a surprise.

## Repo map

```
recipes/NN-name/            docker-compose.yml · .env.example · README.md (one folder per recipe)
tools/smoke.sh              tier 1: all configs + pins · tier 2: live tests of 01, 02, 10
tools/check-pins.sh         fails on unpinned images (compose + Dockerfiles)
.github/workflows/          CI: `docker compose config` on every recipe, pin check, smoke test
```

## Contributing

Found a server that moved, a tag that's stale, or a step that didn't work on your hardware? Issues and PRs are welcome. Run `./tools/smoke.sh` before you push; CI runs the same checks.

---

**Want the reasoning behind every line of these files?** Read [_MCP for the Homelab_](https://axelverne.com) by Axel Verne. MIT-licensed code; the book is $8.99, DRM-free.
