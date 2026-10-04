#!/usr/bin/env bash
# Hook: phi-redaction-check.sh
# Purpose: Block commits that contain unprotected patient Protected Health Information (PHI) in plaintext logs.

set -e

echo "[HOOK] Running PHI Redaction Check..."

# Search for suspicious plaintext logging of health fields in src/
VIOLATIONS=$(grep -rnE 'logger\.(info|debug|warn|error).*([Dd]iagnosis|[Pp]rocedure|[Hh]ealth_[Hh]istory|icd10)' src/ 2>/dev/null || true)

if [ -n "$VIOLATIONS" ]; then
    echo "[ERROR] PHI Leakage Violation Detected in log statements:"
    echo "$VIOLATIONS"
    echo "Protected health information (diagnosis, procedure, clinical history) must NEVER appear in plaintext logs (NFR-03)."
    exit 1
fi

echo "[HOOK] PHI Redaction Check PASSED."
exit 0
