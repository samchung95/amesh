[CmdletBinding()]
param()

$ErrorActionPreference = "Stop"
$RepositoryRoot = Split-Path -Parent $PSScriptRoot
$HookPath = Join-Path $RepositoryRoot ".githooks/pre-push"

if (-not (Test-Path -LiteralPath $HookPath -PathType Leaf)) {
    throw "AMESH hook installer: .githooks/pre-push is missing."
}

$CurrentHooksPath = & git -C $RepositoryRoot config --local --get core.hooksPath
$ReadExitCode = $LASTEXITCODE
if ($ReadExitCode -notin @(0, 1)) {
    throw "AMESH hook installer: could not read core.hooksPath (exit $ReadExitCode)."
}
if ($ReadExitCode -eq 0 -and $CurrentHooksPath -ne ".githooks") {
    throw (
        "AMESH hook installer: core.hooksPath is already '$CurrentHooksPath'; " +
        "refusing to replace it."
    )
}

& git -C $RepositoryRoot config --local core.hooksPath .githooks
if ($LASTEXITCODE -ne 0) {
    throw "AMESH hook installer: could not configure core.hooksPath."
}

$ConfiguredHooksPath = & git -C $RepositoryRoot config --local --get core.hooksPath
if ($LASTEXITCODE -ne 0 -or $ConfiguredHooksPath -ne ".githooks") {
    throw "AMESH hook installer: core.hooksPath verification failed."
}

Write-Output "AMESH hook installer: enabled .githooks/pre-push for this clone."
Write-Output "Ordinary git push commands now run the complete Docker-local gate."
