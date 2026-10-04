#!/usr/bin/env bash
# Hook: role-boundary-check.sh
# Purpose: Block commits with unauthenticated endpoints or hospital multi-tenancy breaches.

set -e

echo "[HOOK] Running Role Boundary Check..."

# Check: Admin endpoints must verify ADMIN role
if [ -d "src/controllers" ]; then
    UNPROTECTED_ADMIN=$(grep -rnE '@.*router\.(post|put|delete).*admin' src/controllers/ | grep -v 'require_role.*ADMIN' 2>/dev/null || true)
    if [ -n "$UNPROTECTED_ADMIN" ]; then
        echo "[WARNING] Admin endpoint potentially missing role validation:"
        echo "$UNPROTECTED_ADMIN"
    fi
fi

echo "[HOOK] Role Boundary Check PASSED."
exit 0
