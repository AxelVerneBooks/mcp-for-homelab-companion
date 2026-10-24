# MCP for the Homelab — Companion Repo

![License: MIT](https://img.shields.io/badge/license-MIT-green) ![Smoke test](https://img.shields.io/badge/smoke%20test-12%20passed%20·%200%20failed-brightgreen) ![Book](https://img.shields.io/badge/book-%248.99%20flat%20·%20DRM%20free-2ea44f)

**This is the free, MIT-licensed companion to [_MCP for the Homelab_](https://axelverne.com)** — the ebook that teaches the why, the scoping ritual, the security model, and the error catalog behind these recipes. The recipes stand alone; the book makes you dangerous.

**Browse the catalog:** [axelvernebooks.github.io/mcp-for-homelab-companion](https://axelvernebooks.github.io/mcp-for-homelab-companion/) (also as [`catalog.json`](docs/catalog.json)).

One folder per recipe from the Recipe Appendix (Chapter 10 of the book). Each folder is self-contained: `cp` the env example, edit it, `docker compose up -d`, wire the stanza, ask the first question.

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
tools/build_docs.py       renders docs/ (GitHub Pages catalog) from recipes/*/recipe.json
tools/validate_metadata.py  schema-checks recipe.json + server.json
docs/                     generated catalog site — don't edit by hand
```

Each recipe folder also carries a `recipe.json` (catalog metadata: status, transport, port, env vars, upstream server). Recipe 10, the one server this repo builds itself, has an [MCP Registry](https://registry.modelcontextprotocol.io) `server.json` as `io.github.AxelVerneBooks/homelab-pool-front-desk`.

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

## Contributing

Bug reports, unsafe-default reports, and recipe requests are welcome — see [CONTRIBUTING.md](CONTRIBUTING.md) for the safety contract every recipe follows.
