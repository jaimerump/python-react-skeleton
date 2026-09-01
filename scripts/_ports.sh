#!/usr/bin/env bash
# Shared port formula -- the single source of truth mirrored from the Tiltfile.
# Sourced by tilt-auto.sh / tilt-cleanup.sh / tilt-cleanup-all.sh.
#
# compute_ports <instance> <increment>  ->  sets DB_PORT API_PORT UI_PORT
#                                            LOCALSTACK_PORT TILT_PORT
compute_ports() {
    local instance="$1" increment="$2" offset
    offset=$(( (instance - 1) * increment ))
    DB_PORT=$((5432 + offset))
    API_PORT=$((8000 + offset))
    UI_PORT=$((5173 + offset))
    LOCALSTACK_PORT=$((4566 + offset))
    TILT_PORT=$((10350 + offset))
}
