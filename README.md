# MCP for the Homelab — Companion Repo

![License: MIT](https://img.shields.io/badge/license-MIT-green) [![recipes](https://github.com/AxelVerneBooks/mcp-for-homelab-companion/actions/workflows/recipes.yml/badge.svg)](https://github.com/AxelVerneBooks/mcp-for-homelab-companion/actions/workflows/recipes.yml) ![Book](https://img.shields.io/badge/book-%248.99%20flat%20·%20DRM%20free-2ea44f)

**This is the free, MIT-licensed companion to [_MCP for the Homelab_](https://axelverne.com)** — the ebook that teaches the why, the scoping ritual, the security model, and the error catalog behind these recipes. The recipes stand alone; the book makes you dangerous.

One folder per recipe from the Recipe Appendix (Chapter 10 of the book). Each folder is self-contained: `cp` the env example, edit it, `docker compose up -d`, wire the stanza, ask the first question.

**New here?** → [**Getting started in 10 minutes**](docs/getting-started.md): one recipe, clone to first answer.

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
  09-grafana-qa/           Grafana MCP (grafana/mcp-grafana)  → HTTP · needs Grafana + viewer token
  10-custom-front-desk/    full working example server        → HTTP · works OOTB (mock backend)
docs/getting-started.md   10-minute end-to-end walkthrough (recipe 10)
tools/smoke.sh            validates all 10 configs; live-tests 01 (mount) + 10 (handshake)
tools/recipe-up.sh        really spins up one recipe (or --all) and talks MCP to it — what CI runs
tools/mcp_probe.py        dependency-free MCP client: initialize → tools/list → tools/call
tools/ci/                 CI-only backends (e.g. a throwaway Grafana) + the unpinned-recipe list
```

**Transport note:** the shelf servers you spawn *from your client* (01, 02) are stdio — no ports, no HTTP. Recipes 03–10 serve streamable HTTP from your compose stack. Every recipe's README shows the correct stanza shape for its transport (book, Chapter 3).

## The 5-minute path (zero external services)

```bash
./tools/smoke.sh
```

The smoke script runs two tiers: **Tier 1** validates every recipe's compose file (syntax + env shape), so a typo anywhere in the repo announces itself; **Tier 2** live-tests the two self-contained recipes — recipe 01's read-only mount against the baked-in demo tree, and recipe 10's *actual MCP handshake* over HTTP against its mock backend. If smoke passes, your Docker setup and the repo's config patterns are sound; everything else is the same pattern pointed at different APIs.

## CI: every recipe, actually spun up

[`.github/workflows/recipes.yml`](.github/workflows/recipes.yml) runs on every push, every PR, and weekly. It runs one clean runner per recipe (`tools/recipe-up.sh <recipe>`): start the real stack, wait for health, then speak MCP to it, including a real tool call. A broken recipe fails the build.

| Recipe | What CI proves |
|---|---|
| 01 | `mcp/filesystem` answers over stdio, lists the demo tree, and **refuses** a write (`EROFS`) |
| 02 | socket visible, `ALLOW_LIST` parsed |
| 09 | `grafana/mcp-grafana` against a throwaway Grafana with a Viewer service-account token: `/healthz` + `search_dashboards` returns seeded data |
| 10 | both containers healthy; MCP handshake + `get_pool_status` round-trips through the mock backend |
| 03–08 | compose config only, flagged with a warning: their server images are still `vX.Y.Z` placeholders, so there's nothing real to pull ([`tools/ci/unpinned.txt`](tools/ci/unpinned.txt)) |

The unpinned list is enforced both ways. If a new placeholder appears, CI fails. If a listed recipe gets pinned, CI also fails until that recipe is removed from the list and given a live probe. Run any of it locally with `./tools/recipe-up.sh 10-custom-front-desk` or `./tools/recipe-up.sh --all`. It uses its own compose project and a temp env file, so your `.env` and running stacks are left alone.

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

Recipes 01 (`mcp/filesystem:1.0.2`), 09 (`grafana/mcp-grafana:2.1.1`) and 10 (built from source) are pinned to releases CI has tested. Every other server image tag is a placeholder of the form `vX.Y.Z`. Before cooking one of those recipes, pin the current release of the referenced server (the book's Chapter 5 explains why pinning is the difference between a stack and a surprise). `grep -r "vX.Y.Z" recipes/` lists everything you must pin.
