$ErrorActionPreference = "Stop"

$cloudflaredUrl = "https://github.com/cloudflare/cloudflared/releases/latest/download/cloudflared-windows-amd64.exe"
$installDir = "C:\Users\manyv\workspace\platforme-osint\cloudflare"
$cloudflaredPath = Join-Path $installDir "cloudflared.exe"

if (Test-Path $cloudflaredPath) {
    $existingSize = (Get-Item $cloudflaredPath).Length
    Write-Host "cloudflared already exists at $cloudflaredPath ($([math]::Round($existingSize/1MB, 1)) MB)" -ForegroundColor Yellow
    $response = Read-Host "Overwrite? (y/n)"
    if ($response -ne "y") {
        Write-Host "Skipping download" -ForegroundColor Yellow
        exit 0
    }
}

Write-Host "Downloading cloudflared from $cloudflaredUrl..." -ForegroundColor Cyan
Write-Host "This may take several minutes depending on network speed..." -ForegroundColor Yellow

$ProgressPreference = "SilentlyContinue"
try {
    Invoke-WebRequest -Uri $cloudflaredUrl -OutFile $cloudflaredPath -UseBasicParsing
} catch {
    Write-Host "Download failed: $_" -ForegroundColor Red
    Write-Host "Trying alternative URL..." -ForegroundColor Yellow
    $altUrl = "https://github.com/cloudflare/cloudflared/releases/download/2024.5.2/cloudflared-windows-amd64.exe"
    Invoke-WebRequest -Uri $altUrl -OutFile $cloudflaredPath -UseBasicParsing
}

if (Test-Path $cloudflaredPath) {
    $sizeMB = [math]::Round((Get-Item $cloudflaredPath).Length / 1MB, 1)
    Write-Host "cloudflared installed successfully at $cloudflaredPath ($sizeMB MB)" -ForegroundColor Green
} else {
    Write-Host "ERROR: cloudflared download failed" -ForegroundColor Red
    exit 1
}

Write-Host "Verifying cloudflared installation..." -ForegroundColor Cyan
& $cloudflaredPath --version

Write-Host ""
Write-Host "cloudflared is ready. Tunnel config is at $installDir\tunnel-config.yml" -ForegroundColor Green
Write-Host "To start the tunnel, run:" -ForegroundColor Yellow
Write-Host "  cd $installDir" -ForegroundColor Yellow
Write-Host "  .\cloudflared.exe tunnel --config tunnel-config.yml run osint-platform" -ForegroundColor Yellow