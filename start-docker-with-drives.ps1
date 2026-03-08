param(
    [switch]$NoStart
)

Set-StrictMode -Version Latest
$ErrorActionPreference = 'Stop'

$repoRoot = Split-Path -Parent $PSCommandPath
Set-Location $repoRoot

$driveInfos = Get-PSDrive -PSProvider FileSystem |
    Where-Object { $_.Root -match '^[A-Za-z]:\\$' } |
    Sort-Object Name

if (-not $driveInfos) {
    throw 'No filesystem drives found to mount.'
}

$overridePath = Join-Path $repoRoot 'docker-compose.drives.yml'
$lines = @(
    'services:',
    '  app:',
    '    volumes:'
)

foreach ($drive in $driveInfos) {
    $letter = $drive.Name.ToLowerInvariant()
    $lines += '      - type: bind'
    $lines += "        source: '$($drive.Root)'"
    $lines += "        target: /mnt/$letter"
}

Set-Content -Path $overridePath -Value ($lines -join [Environment]::NewLine) -Encoding UTF8

Write-Host "Generated $overridePath with $($driveInfos.Count) drive mount(s):"
$driveInfos | ForEach-Object { Write-Host " - $($_.Root) -> /mnt/$($_.Name.ToLowerInvariant())" }

if ($NoStart) {
    Write-Host 'Skipping Docker restart because -NoStart was supplied.'
    exit 0
}

Write-Host 'Restarting Docker app with generated drive mounts...'
docker compose -f docker-compose.yml -f docker-compose.drives.yml down
docker compose -f docker-compose.yml -f docker-compose.drives.yml up --build -d
