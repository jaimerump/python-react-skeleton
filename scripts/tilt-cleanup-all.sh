#!/usr/bin/env bash
# Sweep every instance: down all `app-N` compose projects, then kill leftover PIDs
# on any instance port (both regimes). Safer than the single-instance script -- it
# only kills processes whose name matches an allowlist, so it won't take down an
# unrelated app that happens to share a port.
#
# Usage: scripts/tilt-cleanup-all.sh [--dry-run] [-v]
#   --dry-run  print every action without executing it.
#   -v         also drop named volumes when tearing down projects.
set -euo pipefail

DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ROOT="$(cd "$DIR/.." && pwd)"
# shellcheck source=scripts/_ports.sh
source "$DIR/_ports.sh"

DRY=0
VOLUMES=0
for arg in "$@"; do
    case "$arg" in
        --dry-run) DRY=1 ;;
        -v) VOLUMES=1 ;;
    esac
done

ALLOW='tilt|docker|node|python|uvicorn|postgres|localstack|npm|vite'

act() {  # act <description> <command...>
    if [[ "$DRY" -eq 1 ]]; then
        echo "[dry-run] $1"
    else
        shift
        "$@" 2>/dev/null || true
    fi
}

# 1. Down every discovered app-N compose project (efficient: query by label once).
projects=$(docker ps -aq --filter "label=com.docker.compose.project" \
    | xargs -r docker inspect --format '{{ index .Config.Labels "com.docker.compose.project" }}' 2>/dev/null \
    | sort -u | grep -E '^app-[0-9]+$' || true)

down_flags=(--remove-orphans)
[[ "$VOLUMES" -eq 1 ]] && down_flags+=(-v)
for project in $projects; do
    if [[ "$DRY" -eq 1 ]]; then
        echo "[dry-run] docker compose -p $project down ${down_flags[*]}"
    else
        (
            cd "$ROOT"
            COMPOSE_PROJECT_NAME="$project" API_IMAGE="app_api" UI_IMAGE="app_ui" \
                docker compose -f docker-compose.yml -f docker-compose.localstack.yml \
                down "${down_flags[@]}"
        ) 2>/dev/null || true
    fi
done

# 2. Kill allowlisted leftover PIDs on any instance port (1-99, both regimes).
lsof_args=()
for i in $(seq 1 99); do
    for inc in 1 100; do
        compute_ports "$i" "$inc"
        for p in "$DB_PORT" "$API_PORT" "$UI_PORT" "$LOCALSTACK_PORT" "$TILT_PORT"; do
            lsof_args+=("-i" "tcp:$p")
        done
    done
done

pids=$(lsof -ti "${lsof_args[@]}" 2>/dev/null | sort -u || true)
for pid in $pids; do
    comm=$(ps -p "$pid" -o comm= 2>/dev/null || true)
    [[ -z "$comm" ]] && continue
    if echo "$comm" | grep -Eqi "$ALLOW"; then
        act "kill $pid ($comm)" kill "$pid"
    else
        echo "  skip $pid ($comm) -- not in allowlist"
    fi
done

echo "✓ Sweep complete."
