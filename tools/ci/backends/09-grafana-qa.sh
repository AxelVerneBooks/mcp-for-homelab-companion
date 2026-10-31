# Sourced by tools/recipe-up.sh before the recipe stack starts.
# Boots the throwaway Grafana, then does exactly what the recipe README asks
# a human to do: create a VIEWER service account + token, and point .env at it.
G=http://127.0.0.1:3000
A=admin:ci-admin

compose up -d --quiet-pull --wait grafana

sa_id=$(curl -sf -u "$A" -H 'Content-Type: application/json' \
  -d '{"name":"mcp-ci","role":"Viewer"}' "$G/api/serviceaccounts" \
  | python3 -c 'import sys,json; print(json.load(sys.stdin)["id"])')
token=$(curl -sf -u "$A" -H 'Content-Type: application/json' \
  -d '{"name":"mcp-ci"}' "$G/api/serviceaccounts/$sa_id/tokens" \
  | python3 -c 'import sys,json; print(json.load(sys.stdin)["key"])')

# Seed one dashboard so the probe can prove a real, authenticated read.
curl -sf -u "$A" -H 'Content-Type: application/json' \
  -d '{"dashboard":{"title":"CI Smoke Dashboard","panels":[]},"overwrite":true}' \
  "$G/api/dashboards/db" >/dev/null

set_env GRAFANA_URL http://grafana:3000
set_env GRAFANA_TOKEN "$token"
echo "    -> Grafana up; Viewer service account #$sa_id + token written to env"
