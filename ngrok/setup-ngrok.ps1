$ErrorActionPreference = "Stop"

$authToken = $env:NGROK_AUTH_TOKEN
if (-not $authToken) {
    Write-Host "ERROR: NGROK_AUTH_TOKEN environment variable not set" -ForegroundColor Red
    Write-Host "Set it with: `$env:NGROK_AUTH_TOKEN = 'your_token'"
    exit 1
}

$endpoint = $env:NGROK_ENDPOINT
if (-not $endpoint) {
    Write-Host "ERROR: NGROK_ENDPOINT environment variable not set" -ForegroundColor Red
    exit 1
}

Write-Host "Starting ngrok tunnel to $endpoint..." -ForegroundColor Green
ngrok http 8080 --auth-token=$authToken --url=$endpoint