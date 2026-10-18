$ErrorActionPreference = 'Stop'
$root = (Resolve-Path (Join-Path $PSScriptRoot '..')).Path
$environmentFile = Join-Path $root '.env'

if (-not (Test-Path -LiteralPath $environmentFile)) {
    throw 'Missing .env. Run npm run setup:dev first.'
}

foreach ($line in Get-Content -LiteralPath $environmentFile) {
    if ([string]::IsNullOrWhiteSpace($line) -or $line.TrimStart().StartsWith('#')) { continue }
    $pair = $line.Split('=', 2)
    if ($pair.Length -ne 2) { throw "Invalid .env line: $line" }
    [Environment]::SetEnvironmentVariable($pair[0], $pair[1], 'Process')
}

$apiDirectory = Join-Path $root 'services\core-api'
Push-Location $apiDirectory
try {
    & .\mvnw.cmd spring-boot:run
    exit $LASTEXITCODE
} finally {
    Pop-Location
}
