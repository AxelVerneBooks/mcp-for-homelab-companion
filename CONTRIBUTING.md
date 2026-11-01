# Contributing

This is the free, MIT-licensed companion to [_MCP for the Homelab_](https://axelverne.com) by Axel Verne. Fixes and improvements to the recipes are welcome.

## Before you open a PR

1. Run the smoke test from the repo root and make sure it's green:

   ```bash
   ./tools/smoke.sh
   ```

   Tier 1 validates every recipe's compose file; Tier 2 live-tests recipes 01 and 10.
2. Never commit secrets. Credentials live only in `.env` files (gitignored); `.env.example` files contain placeholders only.
3. Keep image tags as the `vX.Y.Z` placeholder — users pin their own release (see "Versioning rule" in the [README](README.md)).

## Recipe conventions

Each folder under `recipes/` is self-contained: a `docker-compose.yml`, a `.env.example`, and a `README.md`. Recipe READMEs use the same sections, in this order:

- **Overview** — what the server is and what it answers.
- **Requirements** — backend, credentials, env vars, image.
- **Quick start** — the `cp .env.example .env` + validate/`up` commands.
- **Stanza** — the exact `mcpServers` JSON block (`command` for stdio, `url` for HTTP).
- **First question** — the question to ask once it's wired.
- **Scope notes** — the security boundaries for this recipe.
- **Troubleshooting** — known failure modes and fixes.
- **License** — the MIT notice pointing at the root `LICENSE`.

Safety defaults are part of the contract, not style:

- Optional-write servers ship **reads only**; write tools stay commented out with the promotion checklist.
- Filesystem mounts are `:ro`; network-exile where possible.
- Only recipe 02 mounts the Docker socket. A change that makes any other recipe require it will not be accepted.

## License

By contributing, you agree your contributions are licensed under the [MIT License](LICENSE).
