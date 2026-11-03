# Contributing

Thanks for helping keep the recipes accurate. This file covers how pinned
dependencies are kept current. For the recipe conventions themselves, see the
[README](README.md).

## Dependency update policy

### What gets tracked

[Dependabot version updates](https://docs.github.com/en/code-security/dependabot/dependabot-version-updates)
are configured in [`.github/dependabot.yml`](.github/dependabot.yml) for three
ecosystems:

| Ecosystem        | Files scanned                                   | What it bumps          |
|------------------|-------------------------------------------------|------------------------|
| `docker-compose` | `recipes/*/docker-compose.yml`                  | `image:` tags          |
| `docker`         | Dockerfiles under `recipes/*/` (any `*Dockerfile`) | `FROM` base image tags |
| `github-actions` | `.github/workflows/*.yml`                       | `uses:` action refs    |

There are no workflows under `.github/workflows/` yet. The `github-actions`
entry is there so that any workflow added later is tracked from the day it
lands. Until then, Dependabot may report that it found no dependency files for
that ecosystem. That notice is expected.

**Placeholder tags aren't tracked.** Most server images in `recipes/` use the
`vX.Y.Z` placeholder (see the README's "Versioning rule"). That placeholder
isn't a version, so Dependabot can't compare it to anything and won't open PRs
for it. Replace a placeholder with a real released tag and Dependabot will
track it from its next run. Only pin a tag you have confirmed exists in the
image's registry. Don't guess.

**Vulnerability alerts are a separate setting.** Version updates open PRs on a
schedule whether or not a vulnerability is involved. To also get alerts and
security-fix PRs, a maintainer must turn on *Dependabot alerts* and *Dependabot
security updates* under **Settings → Code security**. Security-update PRs use
the same `dependabot.yml` settings.

### How often

- Dependabot checks **weekly, on Mondays**, for every ecosystem.
- It opens at most 10 PRs per ecosystem at a time. GitHub Actions bumps are
  grouped into one PR.
- A maintainer should go through open Dependabot PRs at least once a week. Merge
  security-related bumps first.
- To trigger a check outside the schedule, go to **Insights → Dependency graph →
  Dependabot** and choose *Check for updates*.

### How to test a bump before merging

Never merge a Dependabot PR just because it looks green. A changed tag can
change behavior, and these recipes are meant to be copied into real homelabs.

1. **Read the upstream changes.** Open the release notes or changelog linked in
   the PR body. Look for breaking changes, removed environment variables,
   changed default users or ports, and new required capabilities. Check major
   and minor jumps (for example `alpine:3.20` → `3.21` or `python:3.12-slim` →
   `3.13-slim`) especially closely.
2. **Check out the PR branch locally:**

   ```bash
   git fetch origin pull/<PR-number>/head:dependabot-test
   ```

   ```bash
   git switch dependabot-test
   ```

3. **Run the smoke test from the repo root:**

   ```bash
   ./tools/smoke.sh
   ```

   Tier 1 checks that every recipe's compose file still validates. Tier 2
   live-tests recipe 01 (an `alpine` read-only mount) and recipe 10 (builds both
   `python` Dockerfiles and runs a real MCP `initialize` handshake). Together
   they cover every non-placeholder pin in the repo today. Exit code 0 is
   required.
4. **Exercise the affected recipe directly if smoke doesn't cover it.** For
   example, recipe 02's `socket-check` uses `alpine` but isn't part of the smoke
   run:

   ```bash
   docker compose -f recipes/02-docker-forensics/docker-compose.yml run --rm socket-check
   ```

   If a bump touches a recipe that needs a real backend (03–09), run that
   recipe's validation command from its README against a test instance before
   merging, or say in the PR that it wasn't tested live.
5. **Check the safety defaults still hold** (README, "Safety defaults"): mounts
   still `:ro`, `read_only: true` still honored, and no new socket or network
   requirements.
6. **Merge, or close with a reason.** If a bump breaks a recipe, close the PR
   with a comment explaining why, then tell Dependabot to skip that version
   (comment `@dependabot ignore this minor version` or
   `@dependabot ignore this major version`). Open an issue to track the fix.

### Changing the policy

Edit `.github/dependabot.yml` and update this section in the same PR, so the
documented policy and the real configuration stay in sync.
