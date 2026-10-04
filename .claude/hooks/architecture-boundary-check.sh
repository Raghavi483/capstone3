#!/usr/bin/env bash
# Hook: architecture-boundary-check.sh
# Purpose: Block commits that violate layer dependency directions.

set -e

echo "[HOOK] Running Architecture Boundary Check..."

# Rule: src/domain must never import from src/controllers, src/services, or src/repositories
if [ -d "src/domain" ]; then
    DOMAIN_IMPORTS=$(grep -rnE 'from src\.(controllers|services|repositories)' src/domain/ 2>/dev/null || true)
    if [ -n "$DOMAIN_IMPORTS" ]; then
        echo "[ERROR] Domain layer violation detected! src/domain must not import outer layers:"
        echo "$DOMAIN_IMPORTS"
        exit 1
    fi
fi

# Rule: src/repositories must never import from src/controllers
if [ -d "src/repositories" ]; then
    REPO_IMPORTS=$(grep -rnE 'from src\.controllers' src/repositories/ 2>/dev/null || true)
    if [ -n "$REPO_IMPORTS" ]; then
        echo "[ERROR] Repository layer violation! Cannot import controllers:"
        echo "$REPO_IMPORTS"
        exit 1
    fi
fi

echo "[HOOK] Architecture Boundary Check PASSED."
exit 0
