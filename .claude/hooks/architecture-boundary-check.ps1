# Hook: architecture-boundary-check.ps1
# Purpose: Block commits that violate layer dependency directions.

Write-Host "[HOOK] Running Architecture Boundary Check (PowerShell)..."

if (Test-Path "src/domain") {
    $domainViolations = Get-ChildItem -Path "src/domain" -Recurse -Filter "*.py" | Select-String -Pattern 'from src\.(controllers|services|repositories)'
    if ($domainViolations) {
        Write-Error "[ERROR] Domain layer violation detected! src/domain must not import outer layers:`n$domainViolations"
        exit 1
    }
}

if (Test-Path "src/repositories") {
    $repoViolations = Get-ChildItem -Path "src/repositories" -Recurse -Filter "*.py" | Select-String -Pattern 'from src\.controllers'
    if ($repoViolations) {
        Write-Error "[ERROR] Repository layer violation! Cannot import controllers:`n$repoViolations"
        exit 1
    }
}

Write-Host "[HOOK] Architecture Boundary Check PASSED."
exit 0
