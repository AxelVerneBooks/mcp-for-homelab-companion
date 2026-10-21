#!/usr/bin/env bash
# check-pins.sh — fail if any recipe uses an unpinned image.
#
# Checks every service image (all profiles) and every Dockerfile FROM line.
# Pinned = an explicit version tag (not latest, not the old vX.Y.Z
# placeholder) or an @sha256 digest.
#
# Usage: ./tools/check-pins.sh [recipe-dir ...]   (default: all recipes)
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
[[ $# -gt 0 ]] || set -- "$ROOT"/recipes/*/

bad=0
check() {  # $1 = image ref, $2 = where it came from
  local ref="$1" name tag
  case "$ref" in *@sha256:*) echo "    ✓ $ref ($2)"; return ;; esac
  name="${ref##*/}"
  tag=""; [[ "$name" == *:* ]] && tag="${name##*:}"
  if [[ -z "$tag" || "$tag" == latest || "$tag" == vX.Y.Z ]]; then
    echo "    ✗ unpinned: $ref ($2)"; bad=1
  else
    echo "    ✓ $ref ($2)"
  fi
}

for dir in "$@"; do
  dir="${dir%/}"
  echo "== $(basename "$dir")"
  env_args=()
  [[ -f "$dir/.env.example" ]] && env_args=(--env-file "$dir/.env.example")
  while read -r img; do
    [[ -n "$img" ]] && check "$img" "compose"
  done < <(docker compose --project-directory "$dir" -f "$dir/docker-compose.yml" "${env_args[@]}" \
             --profile '*' config --format json 2>/dev/null \
           | jq -r '.services[] | select(.build == null) | .image')
  for df in "$dir"/*Dockerfile; do
    [[ -f "$df" ]] || continue
    while read -r img; do
      check "$img" "$(basename "$df")"
    done < <(awk 'toupper($1)=="FROM"{for(i=2;i<=NF;i++) if ($i !~ /^--/) {print $i; break}}' "$df")
  done
done

[[ $bad -eq 0 ]] || { echo; echo "unpinned images found"; exit 1; }
