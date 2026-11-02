#!/usr/bin/env bash
# recipe-up.sh — really spin up ONE recipe and prove it answers.
#
# Unlike smoke.sh's Tier 1 (which only validates compose files), this starts
# the recipe's actual stack from a clean slate, waits for health, then talks
# MCP to it (tools/mcp_probe.py): initialize → tools/list → a real tool call.
# This is what CI runs for every recipe (.github/workflows/recipes.yml).
#
# Usage: ./tools/recipe-up.sh 10-custom-front-desk     Exit 0 = recipe works.
#        ./tools/recipe-up.sh --all                     every recipe, in turn
#
# Safe to run locally: it uses its own compose project (ci-<recipe>) and a
# temp env file built from .env.example, so your real .env and running
# stacks are never touched (published ports must be free, though).
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"

if [[ "${1:-}" == "--all" ]]; then
  rc=0
  for dir in "$ROOT"/recipes/*/; do
    "$0" "$(basename "$dir")" || rc=1
    echo
  done
  exit $rc
fi

RECIPE="${1:?usage: recipe-up.sh <recipe-folder-name> | --all}"
RECIPE="${RECIPE%/}"; RECIPE="${RECIPE##*/}"
DIR="$ROOT/recipes/$RECIPE"
[[ -f "$DIR/docker-compose.yml" ]] || { echo "no such recipe: $RECIPE" >&2; exit 2; }

PROBE="python3 $ROOT/tools/mcp_probe.py"
BACKEND="$ROOT/tools/ci/backends/$RECIPE"
ENV_FILE="$(mktemp)"
cp "$DIR/.env.example" "$ENV_FILE"

files=(-f "$DIR/docker-compose.yml")
[[ -f "$BACKEND.yml" ]] && files+=(-f "$BACKEND.yml")

compose() {
  docker compose -p "ci-$RECIPE" --project-directory "$DIR" \
    --env-file "$ENV_FILE" "${files[@]}" "$@"
}
set_env() {  # set_env KEY VALUE — replace KEY in the temp env file
  grep -v "^$1=" "$ENV_FILE" > "$ENV_FILE.tmp" || true
  echo "$1=$2" >> "$ENV_FILE.tmp" && mv "$ENV_FILE.tmp" "$ENV_FILE"
}
annotate() {  # GitHub annotation when in Actions, plain text otherwise
  if [[ -n "${GITHUB_ACTIONS:-}" ]]; then echo "::$1 title=$RECIPE::$2"; else echo "    [$1] $2"; fi
}

cleanup() {
  status=$?
  if [[ $status -ne 0 ]]; then
    echo "    -- container state / logs (last 60 lines each) --"
    compose ps -a 2>/dev/null || true
    compose logs --no-color --tail 60 2>/dev/null || true
  fi
  compose down -v --remove-orphans >/dev/null 2>&1 || true
  rm -f "$ENV_FILE" "$ENV_FILE.tmp"
}
trap cleanup EXIT

echo "== $RECIPE =="

# --- 0. placeholder images: nothing real to spin up yet ----------------------
listed=0; grep -qxF "$RECIPE" "$ROOT/tools/ci/unpinned.txt" && listed=1
placeholder="$(compose config --images | grep 'vX\.Y\.Z' || true)"
if [[ -n "$placeholder" ]]; then
  if [[ $listed -eq 1 ]]; then
    compose config -q
    annotate warning "not spun up: image still a placeholder ($placeholder) — pin a real release to get the live test (tools/ci/unpinned.txt)"
    echo "    ~ SKIPPED (unpinned, compose config valid)"
    exit 0
  fi
  annotate error "placeholder image $placeholder can't be pulled — pin a real release (or, deliberately, list it in tools/ci/unpinned.txt)"
  exit 1
elif [[ $listed -eq 1 ]]; then
  annotate error "listed in tools/ci/unpinned.txt but its images are pinned now — remove it from that file so it gets the live test"
  exit 1
fi

# --- 1. clean slate + backend prep ------------------------------------------
compose down -v --remove-orphans >/dev/null 2>&1 || true
# External networks (e.g. "join your qBit network") must exist before `up`.
for net in $(compose config --format json | python3 -c '
import sys, json
for k, v in (json.load(sys.stdin).get("networks") or {}).items():
    if v.get("external"): print(v.get("name", k))'); do
  docker network inspect "$net" >/dev/null 2>&1 || docker network create "$net" >/dev/null
done
# shellcheck disable=SC1090
[[ -f "$BACKEND.sh" ]] && source "$BACKEND.sh"

# --- 2. spin up + probe ------------------------------------------------------
case "$RECIPE" in
  01-media-librarian)
    # stdio server: the client spawns it, so "up" = a real stdio MCP session
    # through compose (same image, mount and network_mode the recipe defines).
    compose pull -q 2>&1 | grep -v -e Pulling -e Pulled || true
    compose run --rm mount-check | sed 's/^/    /'
    $PROBE --call list_directory --args '{"path":"/media/movies"}' --expect interstellar-2014 \
      --deny write_file --deny-args '{"path":"/media/ci-was-here.txt","content":"x"}' \
      --stdio -- docker compose -p "ci-$RECIPE" --project-directory "$DIR" \
        --env-file "$ENV_FILE" "${files[@]}" run --rm -T media-mcp
    ;;

  02-docker-forensics)
    out="$(compose run --rm socket-check)"
    echo "$out" | sed 's/^/    /'
    grep -q 'socket visible' <<<"$out" && grep -q '^ALLOW_LIST=.\+' <<<"$out" \
      || { echo "    ✗ socket-check output unexpected"; exit 1; }
    echo "    ✓ socket visible, ALLOW_LIST parsed"
    ;;

  09-grafana-qa)
    compose up -d --quiet-pull --wait --wait-timeout 180
    curl -sf --retry 30 --retry-delay 2 --retry-all-errors http://127.0.0.1:9109/healthz >/dev/null
    echo "    ✓ /healthz"
    $PROBE --http http://127.0.0.1:9109/mcp --retry-for 60 \
      --call search_dashboards --args '{"query":"CI Smoke"}' --expect "CI Smoke Dashboard"
    ;;

  10-custom-front-desk)
    compose up -d --build --quiet-pull --wait --wait-timeout 300
    $PROBE --http http://127.0.0.1:9110/mcp --retry-for 60 \
      --call get_pool_status --expect water_temp_c
    ;;

  *)
    annotate error "pinned, but recipe-up.sh has no probe for it yet — add a case so CI can prove it answers"
    exit 1
    ;;
esac

echo "    ✓ PASSED"
