#!/usr/bin/env bash
# smoke.sh — validate the whole companion repo in one pass.
#
# Tier 1: every recipe, no backends needed
#           - `docker compose config` against the recipe's .env.example
#             (syntax, and every variable the file uses is documented)
#           - every image is pinned (tools/check-pins.sh)
# Tier 2: live checks on the self-contained recipes
#           - 01-media-librarian: read-only mount + stdio MCP round trip
#           - 02-docker-forensics: socket gate allows reads, refuses writes
#           - 10-custom-front-desk: MCP handshake + tool call over HTTP
#
# Usage: ./tools/smoke.sh        Exit 0 = green.
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
OUT="$ROOT/tools/.smoke-results"
mkdir -p "$OUT"

pass=0; fail=0
ok()   { echo "    ✓ $1"; pass=$((pass+1)); }
bad()  { echo "    ✗ $1"; fail=$((fail+1)); }

INIT='{"jsonrpc":"2.0","id":1,"method":"initialize","params":{"protocolVersion":"2025-11-25","capabilities":{},"clientInfo":{"name":"smoke","version":"0.2"}}}'
INITIALIZED='{"jsonrpc":"2.0","method":"notifications/initialized"}'

echo "== Tier 1a: compose config validation (all recipes, with .env.example) =="
for dir in "$ROOT"/recipes/*/; do
  name="$(basename "$dir")"
  err="$OUT/$name.config.err"
  if docker compose --project-directory "$dir" -f "$dir/docker-compose.yml" \
       --env-file "$dir/.env.example" config -q 2>"$err" \
     && ! grep -q 'variable is not set' "$err"; then
    ok "$name compose config"
  else
    bad "$name compose config — see $err"
  fi
done

echo
echo "== Tier 1b: image pinning (all recipes) =="
if "$ROOT/tools/check-pins.sh" > "$OUT/pins.txt" 2>&1; then
  ok "every image pinned to a version or digest"
else
  bad "unpinned images — see $OUT/pins.txt"
fi

echo
echo "== Tier 2a: recipe 01 (read-only mount + stdio MCP) =="
R01=(docker compose -f "$ROOT/recipes/01-media-librarian/docker-compose.yml")
if "${R01[@]}" run --rm mount-check > "$OUT/01.mount.txt" 2>&1 \
   && grep -q 'write blocked OK' "$OUT/01.mount.txt"; then
  ok "demo media tree mounted read-only"
else
  bad "mount check failed — see $OUT/01.mount.txt"
fi

{ printf '%s\n' "$INIT" "$INITIALIZED" \
    '{"jsonrpc":"2.0","id":2,"method":"tools/call","params":{"name":"list_directory","arguments":{"path":"/media/movies"}}}' \
    '{"jsonrpc":"2.0","id":3,"method":"tools/call","params":{"name":"write_file","arguments":{"path":"/media/smoke.txt","content":"x"}}}'
  sleep 5; } | "${R01[@]}" run --rm -T media-mcp > "$OUT/01.stdio.txt" 2>/dev/null || true
if grep -q 'interstellar-2014' "$OUT/01.stdio.txt"; then
  ok "stdio list_directory sees the demo tree"
else
  bad "stdio round trip failed — see $OUT/01.stdio.txt"
fi
if grep '"id":3' "$OUT/01.stdio.txt" | grep -q 'EROFS'; then
  ok "stdio write_file refused (EROFS)"
else
  bad "write_file was not refused — see $OUT/01.stdio.txt"
fi

echo
echo "== Tier 2b: recipe 02 (read-only Docker socket gate) =="
R02=(docker compose -f "$ROOT/recipes/02-docker-forensics/docker-compose.yml")
if "${R02[@]}" up -d --quiet-pull socket-proxy > "$OUT/02.up.txt" 2>&1 \
   && "${R02[@]}" run --rm gate-check > "$OUT/02.gate.txt" 2>&1; then
  ok "gate allows reads, refuses writes (403)"
else
  bad "gate check failed — see $OUT/02.gate.txt"
fi
"${R02[@]}" down --remove-orphans >/dev/null 2>&1 || true

echo
echo "== Tier 2c: recipe 10 (MCP over streamable HTTP) =="
R10=(docker compose -f "$ROOT/recipes/10-custom-front-desk/docker-compose.yml")
"${R10[@]}" up -d --build --quiet-pull > "$OUT/10.up.txt" 2>&1 \
  || bad "recipe 10 failed to build/start — see $OUT/10.up.txt"

mcp_post() {  # $1 = JSON-RPC body; extra args go to curl
  local body="$1"; shift
  curl -s -m 15 http://127.0.0.1:9110/mcp \
    -H 'Content-Type: application/json' \
    -H 'Accept: application/json, text/event-stream' "$@" -d "$body"
}

# Wait for uvicorn to actually listen (first boot builds wheels cold).
echo "    -> waiting for :9110 (up to 60s)..."
up=0
for _ in $(seq 1 30); do
  if curl -s -m 3 -o /dev/null "http://127.0.0.1:9110/mcp"; then up=1; break; fi
  sleep 2
done

if [[ $up -eq 1 ]] && mcp_post "$INIT" > "$OUT/10.init.json" \
   && grep -q '"serverInfo' "$OUT/10.init.json"; then
  ok "MCP initialize handshake (serverInfo present)"
else
  bad "no MCP answer on :9110 — see $OUT/10.init.json"
fi

# Full round trip: initialize → initialized → tools/call against the mock API.
sid="$(mcp_post "$INIT" -D - -o /dev/null \
  | tr -d '\r' | awk -F': ' 'tolower($1)=="mcp-session-id"{print $2}')"
if [[ -n "$sid" ]]; then
  mcp_post "$INITIALIZED" -H "Mcp-Session-Id: $sid" -o /dev/null
  mcp_post '{"jsonrpc":"2.0","id":2,"method":"tools/call","params":{"name":"get_pool_status","arguments":{}}}' \
    -H "Mcp-Session-Id: $sid" > "$OUT/10.call.txt" || true
fi
if grep -q 'water_temp_c' "$OUT/10.call.txt" 2>/dev/null; then
  ok "tools/call get_pool_status reached the mock API"
else
  bad "tool call failed — see $OUT/10.call.txt"
fi

echo
echo "== teardown =="
"${R10[@]}" down --remove-orphans >/dev/null 2>&1 || true

echo
echo "smoke: $pass passed, $fail failed"
[[ $fail -eq 0 ]] || exit 1
