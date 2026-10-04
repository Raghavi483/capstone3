# Hook: settlement-cap-check.ps1
# Purpose: Block commits that use floating point numbers in monetary calculation paths or duplicate settlement math.

Write-Host "[HOOK] Running Settlement Cap & Floating-Point Check (PowerShell)..."

if (Test-Path "src/domain") {
    $floatViolations = Get-ChildItem -Path "src/domain" -Recurse -Filter "*.py" | Select-String -Pattern 'float\('
    if ($floatViolations) {
        Write-Error "[ERROR] Floating-point arithmetic detected in domain rules:`n$floatViolations"
        Write-Host "NFR-01 demands fixed-point Decimal arithmetic for all monetary values."
        exit 1
    }
}

if (Test-Path "src/controllers") {
    $dupCalc = Get-ChildItem -Path "src/controllers" -Recurse -Filter "*.py" | Select-String -Pattern 'min\(.*pre_auth.*buffer\)'
    if ($dupCalc) {
        Write-Error "[ERROR] Settlement formula duplication detected in controllers:`n$dupCalc"
        Write-Host "Settlement calculation must be centralized inside src/domain/settlement_rule.py."
        exit 1
    }
}

Write-Host "[HOOK] Settlement Cap Check PASSED."
exit 0
