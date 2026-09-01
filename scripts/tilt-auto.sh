#!/usr/bin/env bash
# Auto-pick the first fully-free instance (dense regime, increment=1) and launch
# Tilt bound to that instance's Tilt-UI port. This is the script that binds the
# Tilt UI to the computed port.
#
# Usage: scripts/tilt-auto.sh [extra tilt args...]
set -euo pipefail

DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ROOT="$(cd "$DIR/.." && pwd)"
# shellcheck source=scripts/_ports.sh
source "$DIR/_ports.sh"

# Ensure a .env exists (the Tiltfile refuses to start without one).
if [[ ! -f "$ROOT/.env" ]]; then
    echo "No .env found; generating one ..."
    "$DIR/generate-env.sh"
fi

port_free() { ! lsof -i "tcp:$1" >/dev/null 2>&1; }

INSTANCE=""
for i in $(seq 1 99); do
    compute_ports "$i" 1
    if port_free "$DB_PORT" && port_free "$API_PORT" && port_free "$UI_PORT" \
        && port_free "$LOCALSTACK_PORT" && port_free "$TILT_PORT"; then
        INSTANCE="$i"
        break
    fi
done

if [[ -z "$INSTANCE" ]]; then
    echo "ERROR: no free instance found in 1-99." >&2
    exit 1
fi

compute_ports "$INSTANCE" 1
echo "Launching instance $INSTANCE (dense regime):"
echo "  API       -> http://localhost:$API_PORT"
echo "  UI        -> http://localhost:$UI_PORT"
echo "  LocalStack-> http://localhost:$LOCALSTACK_PORT"
echo "  Tilt UI   -> http://localhost:$TILT_PORT"

export INSTANCE
export TILT_PORT_INCREMENT=1
cd "$ROOT"
exec tilt up --port "$TILT_PORT" "$@"
