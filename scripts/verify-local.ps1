[CmdletBinding()]
param(
    [ValidateSet(
        "all",
        "core",
        "backend",
        "frontend",
        "harness",
        "contracts",
        "format",
        "frontend-lint",
        "review",
        "compose",
        "image",
        "package"
    )]
    [string]$Suite = "all"
)

$ErrorActionPreference = "Stop"
$RepositoryRoot = Split-Path -Parent $PSScriptRoot

function Invoke-DockerCommand {
    param([Parameter(Mandatory)][string[]]$DockerArguments)

    & docker @DockerArguments
    if ($LASTEXITCODE -ne 0) {
        throw "docker command failed with exit code $LASTEXITCODE"
    }
}

function Invoke-CoreSuite {
    param([Parameter(Mandatory)][string]$Name)

    Invoke-DockerCommand @(
        "compose", "-f", "compose.verify.yaml", "run", "--rm", "--build", "verify", $Name
    )
}

function Test-ComposeFiles {
    Invoke-DockerCommand @("compose", "config", "--quiet")
    Invoke-DockerCommand @("compose", "-f", "compose.compact.yaml", "config", "--quiet")
    Invoke-DockerCommand @("compose", "-f", "compose.verify.yaml", "config", "--quiet")

    $variables = @{
        AMESH_DATABASE_URL = "postgresql://amesh@postgres:5432/amesh"
        AMESH_DATABASE_TLS_MODE = "disable"
        AMESH_POSTGRES_DB = "amesh"
        AMESH_POSTGRES_USER = "amesh"
        AMESH_HARDENED_SECRETS_DIR = "."
    }
    $previous = @{}
    foreach ($name in $variables.Keys) {
        $previous[$name] = [Environment]::GetEnvironmentVariable($name, "Process")
        [Environment]::SetEnvironmentVariable($name, $variables[$name], "Process")
    }
    try {
        Invoke-DockerCommand @("compose", "-f", "compose.hardened.yaml", "config", "--quiet")
    }
    finally {
        foreach ($name in $variables.Keys) {
            [Environment]::SetEnvironmentVariable($name, $previous[$name], "Process")
        }
    }
}

function Test-ProductionImage {
    Invoke-DockerCommand @("build", "-t", "amesh:harness-conformance", ".")
    Invoke-DockerCommand @(
        "run", "--rm", "--entrypoint", "python",
        "amesh:harness-conformance", "-m", "amesh.harness_probe"
    )
}

function New-ReleaseArchives {
    Invoke-DockerCommand @(
        "compose", "-f", "compose.verify.yaml", "run", "--rm", "--build", "package"
    )
}

Push-Location $RepositoryRoot
try {
    switch ($Suite) {
        "all" {
            Invoke-CoreSuite "all"
            Test-ComposeFiles
            Test-ProductionImage
            New-ReleaseArchives
        }
        "core" { Invoke-CoreSuite "all" }
        "backend" { Invoke-CoreSuite "backend" }
        "frontend" { Invoke-CoreSuite "frontend" }
        "harness" { Invoke-CoreSuite "harness" }
        "contracts" { Invoke-CoreSuite "contracts" }
        "format" { Invoke-CoreSuite "format" }
        "frontend-lint" { Invoke-CoreSuite "frontend-lint" }
        "review" { Invoke-CoreSuite "review" }
        "compose" { Test-ComposeFiles }
        "image" { Test-ProductionImage }
        "package" { New-ReleaseArchives }
    }
}
finally {
    Pop-Location
}
