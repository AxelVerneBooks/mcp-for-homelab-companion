#!/usr/bin/env bash
# smoke.sh — validate the whole companion repo in one pass.
#
# Tier 1: `docker compose config` validates every recipe (syntax, env shape).
# Tier 2: live checks on the two recipes that are self-contained:
#           - 01-media-librarian: mount-check (demo tree readable, read-only)
#           - 10-custom-front-desk: full MCP initialize handshake over HTTP
#
# Usage: ./tools/smoke.sh        Exit 0 = green.
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
OUT="$ROOT/tools/.smoke-results"
mkdir -p "$OUT"

pass=0; fail=0
ok()   { echo "    ✓ $1"; pass=$((pass+1)); }
bad()  { echo "    ✗ $1"; fail=$((fail+1)); }

echo "== Tier 1: compose config validation (all recipes) =="
for dir in "$ROOT"/recipes/*/; do
  name="$(basename "$dir")"
  if docker compose -f "$dir/docker-compose.yml" config -q 2>"$OUT/$name.config.err"; then
    ok "$name compose config"
  else
    bad "$name compose config — see $OUT/$name.config.err"
  fi
done

echo
echo "== Tier 2a: recipe 01 mount check (read-only demo tree) =="
if docker compose -f "$ROOT/recipes/01-media-librarian/docker-compose.yml" \
    run --rm mount-check > "$OUT/01.mount.txt" 2>&1; then
  ok "demo media tree mounted read-only"
else
  bad "mount check failed — see $OUT/01.mount.txt"
fi

echo
echo "== Tier 2b: recipe 10 MCP handshake (streamable HTTP) =="
docker compose -f "$ROOT/recipes/10-custom-front-desk/docker-compose.yml" \
  up -d --build --quiet-pull >/dev/null 2>&1 || { bad "recipe 10 failed to build/start"; }

# Wait for uvicorn to actually listen (first boot builds wheels cold).
echo "    -> waiting for :9110 (up to 30s)..."
up=0
for i in $(seq 1 15); do
  if curl -sf -m 3 -o /dev/null "http://127.0.0.1:9110/mcp" \
      -H 'Content-Type: application/json' \
      -H 'Accept: application/json, text/event-stream' \
      -d '{"jsonrpc":"2.0","id":0,"method":"ping"}' 2>/dev/null \
     || curl -s -m 3 -o /dev/null "http://127.0.0.1:9110/" 2>/dev/null; then
    up=1; break
  fi
  sleep 2
done

if [[ $up -eq 1 ]] && curl -sf -m 15 http://127.0.0.1:9110/mcp \
    -H 'Content-Type: application/json' \
    -H 'Accept: application/json, text/event-stream' \
    -d '{"jsonrpc":"2.0","id":1,"method":"initialize","params":{"protocolVersion":"2026-07-28","capabilities":{},"clientInfo":{"name":"smoke","version":"0.1"}}}' \
    > "$OUT/10.init.json"; then
  if grep -q '"serverInfo' "$OUT/10.init.json"; then
    ok "MCP initialize handshake (serverInfo present)"
  else
    bad "handshake body unexpected — see $OUT/10.init.json"
  fi
else
  bad "no MCP answer on :9110 — see $OUT/10.init.json"
fi

echo
echo "== teardown =="
docker compose -f "$ROOT/recipes/10-custom-front-desk/docker-compose.yml" \
  down --remove-orphans >/dev/null 2>&1 || true

echo
echo "smoke: $pass passed, $fail failed"
[[ $fail -eq 0 ]] || exit 1
