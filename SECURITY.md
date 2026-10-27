# Security Policy

These recipes hand an AI assistant a set of keys to your homelab. The
conventions below exist so that every recipe hands over as few keys as
possible, and so the containers holding them are as boring as possible to
attack. They follow the book's Chapter 7 rules; this file is the
checklist form.

## Reporting a vulnerability

**Please don't open a public issue for a security problem.**

Report it privately through GitHub's private vulnerability reporting:
go to the repo's **Security** tab, then **Report a vulnerability**. Include:

- the recipe (folder name) and file affected,
- what an attacker can do, and from where (LAN, the MCP client, a
  compromised backend, the internet),
- steps to reproduce, or a proof-of-concept compose/stanza diff,
- your suggested fix, if you have one.

You should get an acknowledgement within 7 days. Once a fix is merged, the
advisory is published with credit to you, unless you'd rather stay
anonymous.

**In scope:** anything in this repo, meaning the compose files, Dockerfiles,
`server.py`/`mock-api.py`, client stanzas in the READMEs, `tools/smoke.sh`,
and any advice in the docs that would leave a reader exposed if they
followed it.

**Out of scope:** vulnerabilities in the third-party MCP servers or the
services the recipes point at (Home Assistant, Proxmox, Pi-hole, and so on).
Report those upstream. We still want to hear about them if a recipe should
pin around a vulnerable release or change a default, so tell us that part.

## Hardening conventions (every recipe follows these)

A new or changed recipe that breaks one of these rules needs a comment in
the compose file explaining why, and an entry under
[Documented exceptions](#documented-exceptions).

### 1. Images are pinned, never `latest`

- Never use `:latest`, and never leave an image untagged (untagged means
  `latest`).
- Pin to an **exact release**, e.g. `alpine:3.20.3` or
  `python:3.12.7-slim-bookworm`, not a floating major/minor like
  `alpine:3.20` or `python:3.12-slim`.
- Third-party MCP server images ship as `vX.Y.Z` placeholders on purpose.
  `grep -r "vX.Y.Z" recipes/` lists what you must pin before running. Pick
  a release, read its changelog, and pin it.
- For real deployments, pin by digest as well (`image@sha256:...`). Tags are
  mutable; digests aren't.
- Bump versions on purpose (read the changelog, re-run the smoke test). Never
  let a restart pull something new.

### 2. Containers run as non-root

Every service uses the shared baseline at the top of its compose file:

```yaml
x-hardening: &hardening
  user: "${PUID:-65534}:${PGID:-65534}"   # nobody:nogroup unless overridden
  read_only: true                          # immutable root filesystem
  tmpfs: [/tmp]                            # the only writable scratch space
  cap_drop: [ALL]                          # no Linux capabilities
  security_opt: ["no-new-privileges:true"] # setuid binaries can't escalate
  mem_limit: 256m
  cpus: 0.50
  pids_limit: 128
```

- The default is UID/GID `65534` (`nobody`). Override with `PUID`/`PGID` in
  `.env` only when a mount needs it, e.g. media that isn't world-readable.
  Set it to a dedicated low-privilege user, **never `0`**.
- Images built in this repo (recipe 10) also set `USER 65534:65534` in the
  Dockerfile, so they're non-root even outside compose. Code stays
  root-owned, so the process can't rewrite itself.
- stdio stanzas (`docker run` in a recipe README) carry the same flags:
  `--user`, `--read-only`, `--tmpfs /tmp`, `--cap-drop ALL`,
  `--security-opt no-new-privileges:true`, and the resource flags.
- No `privileged: true`, no `cap_add`, no `network_mode: host`, no
  `pid: host`.

If a pinned upstream image refuses to start read-only (it writes a cache to
`$HOME`, say), add a narrowly scoped `tmpfs:` path for that directory.
Don't drop `read_only`.

### 3. Every container has resource limits

- `mem_limit`, `cpus`, and `pids_limit` are set on every service. The
  defaults (256 MiB, half a core, 128 PIDs) are plenty for an MCP server
  that proxies API calls.
- The point is containment. A runaway loop, a fork bomb, or an assistant
  asking for "everything since 2019" can't starve the host running your
  NAS and your DNS.
- Raise a limit in the recipe's compose file only when a real workload
  needs it, and leave a comment saying why.

### 4. Ports

- **Only publish what a client has to reach.** stdio servers (01, 02)
  publish nothing. Backends that only the MCP server talks to (recipe 10's
  `pool-api`) publish nothing and are reached over a private compose network.
- **Published ports bind to loopback by default:**

  ```yaml
  ports:
    - "${MCP_BIND_ADDR:-127.0.0.1}:9103:9103"
  ```

  A bare `"9103:9103"` binds every interface. That includes any public or
  VPN interface on the host, and Docker's iptables rules bypass most host
  firewalls (`ufw`, `firewalld`).
- If your MCP client is on another machine, set `MCP_BIND_ADDR` in `.env`
  to the Docker host's **LAN IP**. Don't use `0.0.0.0` on a host that has a
  public interface. For anything that leaves your LAN, put the server
  behind a reverse proxy with TLS and authentication, or a VPN such as
  WireGuard or Tailscale. These servers have no auth of their own.
- One port per recipe, in the `91NN` range matching the recipe number, so a
  stray listener is easy to attribute (`ss -tlnp | grep 91`).

### 5. Network isolation

- Give a server the narrowest network it needs: `network_mode: none` when it
  touches only mounts (01, 02), an isolated or external network shared only
  with its backend when it talks to one app (03, 05, 10), otherwise the
  recipe's own default project network.
- Never attach an MCP server to a network shared with unrelated services
  "just in case".

### 6. Secrets

- Credentials come only from `.env` (gitignored). `.env.example` files hold
  placeholders, never real values.
- Each recipe uses a **dedicated, least-privilege account or token** on the
  backend: Viewer, PVEAuditor, read-only API key, houseguest-scoped HA user.
  Never use your personal or admin credentials.
- Nothing secret goes in a Dockerfile, a compose `environment:` literal, or
  a client stanza.

### 7. Mounts and the Docker socket

- Data mounts are `:ro` unless a recipe's README explains the write and its
  promotion checklist.
- Only recipe 02 mounts `/var/run/docker.sock`. Any other recipe that asks
  for it is a bug: report it, don't run it.
- `:ro` on the socket does **not** make the Docker API read-only. Anyone who
  can open the socket controls the daemon, which is effectively root on the
  host. The server's `ALLOW_LIST` is the real boundary.

### 8. Write tools ship disabled

Every server starts read-only. Write tools stay commented out or unscoped
until a clean week of reads, then go through the promotion checklist in the
recipe README (book, Chapters 5–7).

## Documented exceptions

| Recipe | Rule | Why |
|---|---|---|
| 02-docker-forensics (client stanza) | Runs as the image's default user, not forced to `nobody` | The Docker socket is `root:docker`. To run unprivileged, pass `--user 65534:<docker-gid>`. Socket access is root-equivalent either way, so `ALLOW_LIST` is the boundary. |

## Checking a recipe

```bash
./tools/smoke.sh                                   # all recipes validate; 01 + 10 run live
grep -rn "latest" recipes/                         # should print nothing
grep -rn "vX.Y.Z" recipes/                         # placeholders you must pin
docker compose -f recipes/<r>/docker-compose.yml config | grep -E "host_ip|user|read_only|mem_limit"
```
