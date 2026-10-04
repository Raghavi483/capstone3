#!/usr/bin/env bash
# Hook: settlement-cap-check.sh
# Purpose: Block commits that use floating point numbers in monetary calculation paths or duplicate settlement math.

set -e

echo "[HOOK] Running Settlement Cap & Floating-Point Check..."

# Check 1: Ensure domain settlement calculation doesn't use float()
if [ -d "src/domain" ]; then
    FLOAT_VIOLATIONS=$(grep -rnE 'float\(' src/domain/ 2>/dev/null || true)
    if [ -n "$FLOAT_VIOLATIONS" ]; then
        echo "[ERROR] Floating-point arithmetic detected in domain rules:"
        echo "$FLOAT_VIOLATIONS"
        echo "NFR-01 demands fixed-point Decimal arithmetic for all monetary values."
        exit 1
    fi
fi

# Check 2: Ensure settlement formula is not duplicated in controllers or services
DUPLICATE_CALC=$(grep -rnE 'min\(.*pre_auth.*buffer\)' src/controllers/ 2>/dev/null || true)
if [ -n "$DUPLICATE_CALC" ]; then
    echo "[ERROR] Settlement formula duplication detected in controllers:"
    echo "$DUPLICATE_CALC"
    echo "Settlement calculation must be centralized inside src/domain/settlement_rule.py."
    exit 1
fi

echo "[HOOK] Settlement Cap Check PASSED."
exit 0
