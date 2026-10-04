# Hook: phi-redaction-check.ps1
# Purpose: Block commits that contain unprotected patient Protected Health Information (PHI) in plaintext logs.

Write-Host "[HOOK] Running PHI Redaction Check (PowerShell)..."

if (Test-Path "src") {
    $violations = Get-ChildItem -Path "src" -Recurse -Filter "*.py" | Select-String -Pattern 'logger\.(info|debug|warn|error).*([Dd]iagnosis|[Pp]rocedure|[Hh]ealth_[Hh]istory|icd10)'
    if ($violations) {
        Write-Error "[ERROR] PHI Leakage Violation Detected in log statements:`n$violations"
        Write-Host "Protected health information (diagnosis, procedure, clinical history) must NEVER appear in plaintext logs (NFR-03)."
        exit 1
    }
}

Write-Host "[HOOK] PHI Redaction Check PASSED."
exit 0
