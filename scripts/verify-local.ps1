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
        "docs",
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
    Invoke-DockerCommand @("compose", "-f", "compose.docs.yaml", "config", "--quiet")

    $variables = @{
        AMESH_DATABASE_URL = "postgresql://amesh@postgres:5432/amesh"
        AMESH_DATABASE_TLS_MODE = "disable"
        AMESH_POSTGRES_DB = "amesh"
        AMESH_POSTGRES_USER = "amesh"
        AMESH_HARDENED_SECRETS_DIR = "."
        AMESH_SESSION_DATABASE_URL = "postgresql+asyncpg://db.internal/amesh"
        AMESH_SESSION_DATABASE_TLS_MODE = "verify-full"
        AMESH_SESSION_OBJECT_STORAGE_ENDPOINT = "https://s3.internal"
        AMESH_SESSION_OBJECT_STORAGE_REGION = "us-east-1"
        AMESH_SESSION_OBJECT_STORAGE_BUCKET = "amesh"
        AMESH_SESSION_EGRESS_ALLOWED_HOSTS = '["s3.internal"]'
        AMESH_SESSION_SECRETS_DIR = ".session-secrets"
    }
    $previous = @{}
    foreach ($name in $variables.Keys) {
        $previous[$name] = [Environment]::GetEnvironmentVariable($name, "Process")
        [Environment]::SetEnvironmentVariable($name, $variables[$name], "Process")
    }
    try {
        Invoke-DockerCommand @("compose", "-f", "compose.hardened.yaml", "config", "--quiet")
        Invoke-DockerCommand @(
            "compose", "-f", "compose.session-orchestrator.yaml", "config", "--quiet"
        )
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
        "docs" { Invoke-CoreSuite "docs" }
        "compose" { Test-ComposeFiles }
        "image" { Test-ProductionImage }
        "package" { New-ReleaseArchives }
    }
}
finally {
    Pop-Location
}
