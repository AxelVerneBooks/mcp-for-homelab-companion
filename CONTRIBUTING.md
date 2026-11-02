# Contributing

Thanks for helping. This repo is the free, MIT-licensed companion to [_MCP for the Homelab_](https://axelverne.com); every recipe has to stand alone for someone who has never read the book, and stay safe for someone who copy-pastes it at 2 a.m.

## Ways to help

- **Report a broken recipe** — use the [“Recipe doesn't work”](https://github.com/AxelVerneBooks/mcp-for-homelab-companion/issues/new?template=recipe-bug.yml) form. Include the image tag you pinned and your backend version; redact every token.
- **Report an unsafe default** — a mount that should be `:ro`, a write tool that's live, a recipe that wants the Docker socket. These get fixed first.
- **Request a recipe** — tell us the service and the *first question* you'd ask it.
- **Fix or add a recipe** — open a PR (below).

## Ground rules (non-negotiable)

These are the repo's safety contract. A PR that breaks one won't merge, however useful it is.

1. **Read-only by default.** Write tools ship commented out, with the promotion checklist next to them (see `recipes/10-custom-front-desk/server.py`).
2. **Secrets only from `.env`.** `.env.example` holds placeholders, never real credentials. `.env` is gitignored — keep it that way.
3. **Narrowest mount and network.** Filesystem mounts are `:ro`. Use `network_mode: none` or an isolated compose network wherever the server allows.
4. **The Docker socket belongs to recipe 02 only.** Any other recipe that needs it is a bug.
5. **Dedicated, least-privilege credentials.** The README says which role/user to create (Viewer, PVEAuditor, houseguest user…), never “use your admin token.”
6. **Placeholder image tags.** Images use `vX.Y.Z`; readers pin the current release themselves.

## Recipe anatomy

```
recipes/NN-short-name/
  README.md            status line, Run, Stanza (first ```json block), First question, Scope notes
  docker-compose.yml   name: mcp-recipe-NN; validates with `docker compose config -q`
  .env.example         every variable the compose file reads, with comments
  recipe.json          catalog metadata (schema: tools/schemas/recipe.schema.json)
  server.json          only for servers this repo builds and publishes (see below)
```

Copy the closest existing recipe and edit it. Ports follow the pattern `91NN` for recipe `NN`.

### `recipe.json`

Drives the [docs site](https://axelvernebooks.github.io/mcp-for-homelab-companion/) and `docs/catalog.json`. Environment-variable fields (`name`, `description`, `isRequired`, `isSecret`, `placeholder`, `default`) mirror the MCP Registry `server.json` format.

Under `upstream`, set `registryName` and `repository` **only** when the recipe is built for one specific published server (check [registry.modelcontextprotocol.io](https://registry.modelcontextprotocol.io)). For “community server — pin your choice” recipes, leave them out; don't endorse a server you haven't tested.

### `server.json` (MCP Registry)

Only recipes whose server code lives in this repo get a `server.json` — today that's recipe 10. Recipes 01–09 wrap other people's servers; those servers are published to the registry by their own maintainers, under their own namespaces, so we link to them from `recipe.json` instead.

To publish a new version of recipe 10:

1. Bump `version` and the image tag in `packages[0].identifier` in `recipes/10-custom-front-desk/server.json`.
2. Merge, then push the tag `front-desk-v<version>`. The `publish-front-desk` workflow builds and pushes the image to GHCR and runs `mcp-publisher publish` (GitHub OIDC, namespace `io.github.AxelVerneBooks`).
3. First release only: make the GHCR package public so the registry can verify the image's `io.modelcontextprotocol.server.name` label.

## Before you open a PR

```bash
./tools/smoke.sh                     # compose validation + live tests for 01 and 10
pip install jsonschema
python3 tools/validate_metadata.py   # recipe.json / server.json schemas, env vars ↔ compose
python3 tools/build_docs.py          # regenerate docs/ and commit the result
```

CI runs the last two (with `--check`) plus `docker compose config` on every recipe.

## Docs site

`docs/` is generated — edit `recipe.json`, the recipe README's stanza, or `tools/build_docs.py`, never `docs/index.html` directly. GitHub Pages serves `docs/` from `main` (Settings → Pages → Deploy from a branch → `main` / `/docs`).

## License

By contributing you agree your work is released under the repo's [MIT license](LICENSE).
