#!/usr/bin/env bash
# Source .env and exec a command with the same env the stack uses.
# Usage: scripts/run-with-env.sh <command> [args...]
#   e.g. scripts/run-with-env.sh uv run python -m app.worker
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
ENV_FILE="$ROOT/.env"

if [[ ! -f "$ENV_FILE" ]]; then
    echo "ERROR: $ENV_FILE not found. Run scripts/generate-env.sh first." >&2
    exit 1
fi
if [[ $# -eq 0 ]]; then
    echo "Usage: scripts/run-with-env.sh <command> [args...]" >&2
    exit 1
fi

set -a
# shellcheck disable=SC1090
source "$ENV_FILE"
set +a

exec "$@"
