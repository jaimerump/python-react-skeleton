#!/usr/bin/env bash
# Tear down a single instance: stop Docker first (while it's responsive), then
# kill any leftover host PIDs still holding that instance's ports.
#
# Usage: scripts/tilt-cleanup.sh [-v] [instance]
#   -v   also drop the instance's named volumes (postgres_data, ui_node_modules).
set -euo pipefail

DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ROOT="$(cd "$DIR/.." && pwd)"
# shellcheck source=scripts/_ports.sh
source "$DIR/_ports.sh"

VOLUMES=0
INSTANCE=1
for arg in "$@"; do
    case "$arg" in
        -v) VOLUMES=1 ;;
        *) INSTANCE="$arg" ;;
    esac
done

PROJECT="app-$INSTANCE"
echo "Tearing down $PROJECT ..."

# The compose project name only depends on the instance number (not the port
# regime), so `down -p` cleans containers/volumes regardless of increment.
down_flags=(--remove-orphans)
[[ "$VOLUMES" -eq 1 ]] && down_flags+=(-v)
(
    cd "$ROOT"
    COMPOSE_PROJECT_NAME="$PROJECT" API_IMAGE="app_api" UI_IMAGE="app_ui" \
        docker compose -f docker-compose.yml -f docker-compose.localstack.yml \
        down "${down_flags[@]}"
) 2>/dev/null || true

# Kill leftover PIDs on this instance's ports across both regimes.
for inc in 1 100; do
    compute_ports "$INSTANCE" "$inc"
    for port in "$DB_PORT" "$API_PORT" "$UI_PORT" "$LOCALSTACK_PORT" "$TILT_PORT"; do
        pids=$(lsof -ti "tcp:$port" 2>/dev/null || true)
        if [[ -n "$pids" ]]; then
            echo "  killing PIDs on :$port -> $pids"
            # shellcheck disable=SC2086
            kill $pids 2>/dev/null || true
        fi
    done
done

echo "✓ $PROJECT torn down."
