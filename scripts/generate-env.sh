#!/usr/bin/env bash
# Render .env for local development. Two modes, chosen automatically:
#   1. Shared secrets: if ~/.app/.env exists, copy it to .env (idempotent via cmp).
#   2. Template render: otherwise render .env.template, substituting each
#      {{VAR}} from the same-named shell env var. Missing vars are left literal
#      and reported -- this script warns, never fails.
#
# Usage: scripts/generate-env.sh [-f]
#   -f   overwrite an existing .env in template-render mode.
set -euo pipefail

FORCE=0
[[ "${1:-}" == "-f" ]] && FORCE=1

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
ENV_FILE="$ROOT/.env"
TEMPLATE="$ROOT/.env.template"
SHARED="$HOME/.app/.env"

# Mode 1: shared secrets file outside any checkout.
if [[ -f "$SHARED" ]]; then
    if [[ -f "$ENV_FILE" ]] && cmp -s "$SHARED" "$ENV_FILE"; then
        echo "✓ .env already matches $SHARED (no change)."
    else
        cp "$SHARED" "$ENV_FILE"
        echo "✓ Copied $SHARED -> .env"
    fi
    exit 0
fi

# Mode 2: template render.
if [[ ! -f "$TEMPLATE" ]]; then
    echo "ERROR: $TEMPLATE not found." >&2
    exit 1
fi
if [[ -f "$ENV_FILE" && "$FORCE" -ne 1 ]]; then
    echo "✓ .env exists; leaving it untouched (pass -f to regenerate from template)."
    exit 0
fi

missing=()
while IFS= read -r line || [[ -n "$line" ]]; do
    # Leave comments and non-placeholder lines untouched.
    if [[ "$line" == \#* ]] || [[ ! "$line" =~ \{\{([A-Za-z_][A-Za-z0-9_]*)\}\} ]]; then
        printf '%s\n' "$line"
        continue
    fi
    ph="${BASH_REMATCH[1]}"
    val="${!ph:-}"
    if [[ -z "$val" ]]; then
        missing+=("$ph")
        printf '%s\n' "$line"          # keep {{...}} literal
    else
        printf '%s\n' "${line//\{\{$ph\}\}/$val}"
    fi
done < "$TEMPLATE" > "$ENV_FILE"

echo "✓ Rendered .env.template -> .env"
if (( ${#missing[@]} )); then
    echo "WARN: unset placeholders left literal: ${missing[*]}" >&2
fi
