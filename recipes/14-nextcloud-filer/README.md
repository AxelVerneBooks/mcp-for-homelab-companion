# Recipe 14 — Nextcloud Filer

**Status:** ⚠️ Needs backend (Nextcloud + app password) · **Book ref:** companion-only recipe (not in the Chapter 10 appendix); follows the Chapter 5 scoping pattern

An MCP server over Nextcloud files. Where recipe 01 reads a local directory, this one reads what the family actually syncs — the shared folders on everyone's phones and laptops — through Nextcloud's own APIs, with Nextcloud's own sharing as the permission boundary.

## Run

```bash
cp .env.example .env               # NC_URL + dedicated user + app password
docker compose run --rm preflight  # verify reachability + credentials before anything else
docker compose up -d
```

## Verify

`preflight` makes two calls from inside a container:

1. `GET $NC_URL/status.php` — no auth; prints `"installed":true` and `"maintenance":false` on a healthy instance.
2. `GET $NC_URL/ocs/v2.php/cloud/user?format=json` with basic auth (user + app password) and the `OCS-APIRequest: true` header — proves the credentials work and prints the user id.

Expected output:

```
reachable: "installed":true, "maintenance":false
app password OK, acting as: "id":"mcp-bot"
```

- `400 Bad Request` on step 1 → most often the hostname in `NC_URL` is not in Nextcloud's `trusted_domains`. Add it in `config/config.php`, or use a hostname that's already listed.
- `401` on step 2 → wrong user or app password (or the app password was revoked).

The same checks by hand:

```bash
curl -s "$NC_URL/status.php"
curl -s -u "$NC_USER:$NC_APP_PASSWORD" -H 'OCS-APIRequest: true' "$NC_URL/ocs/v2.php/cloud/user?format=json"
```

## Stanza

```json
{ "mcpServers": { "nextcloud-filer": {
    "url": "http://<docker-host>:9114/mcp" } } }
```

## First question

*"What changed in the shared Taxes folder this month, and is anything in it a duplicate?"*

## Scope notes

- **Dedicated user, read-only shares.** Create a user for the assistant, then share only the folders it should read with that user, with editing turned off. Nextcloud enforces the share permissions server-side, so a write tool would be refused even if the MCP server offered one.
- **App password, never the login password.** App passwords are revocable one by one (Personal settings → Security → Devices & sessions) and can't change the account's password — revoke it and the server is cut off without touching anything else.
- Don't put the dedicated user in the `admin` group. Admin reach in Nextcloud includes user management and app installs.
