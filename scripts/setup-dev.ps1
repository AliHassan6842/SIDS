param([switch]$Force)

$ErrorActionPreference = 'Stop'
$root = (Resolve-Path (Join-Path $PSScriptRoot '..')).Path
$target = Join-Path $root '.env'
$example = Join-Path $root '.env.example'

if ((Test-Path -LiteralPath $target) -and -not $Force) {
    Write-Host '.env already exists; use -Force only when you intentionally want to rotate local development secrets.'
    exit 0
}

function New-RandomSecret([int]$bytes = 32) {
    $buffer = New-Object byte[] $bytes
    [Security.Cryptography.RandomNumberGenerator]::Fill($buffer)
    return [Convert]::ToBase64String($buffer).TrimEnd('=').Replace('+', '-').Replace('/', '_')
}

$content = Get-Content -LiteralPath $example -Raw
$content = $content.Replace('replace-with-a-random-development-password', (New-RandomSecret 24))
$content = $content.Replace('replace-with-at-least-32-random-characters', (New-RandomSecret 40))
$content = $content.Replace('replace-with-at-least-24-random-characters', (New-RandomSecret 32))
[IO.File]::WriteAllText($target, $content, [Text.UTF8Encoding]::new($false))
Write-Host 'Created ignored .env with generated local development secrets.'
