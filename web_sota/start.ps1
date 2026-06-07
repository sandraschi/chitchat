Param([switch]$Headless)

# --- SOTA Headless Standard ---
if ($Headless -and ($Host.UI.RawUI.WindowTitle -notmatch 'Hidden')) {
    Start-Process pwsh -ArgumentList '-NoProfile', '-File', $PSCommandPath, '-Headless' -WindowStyle Hidden
    exit
}
$WindowStyle = if ($Headless) { 'Hidden' } else { 'Normal' }

$ErrorActionPreference = "Stop"
$root = Split-Path -Parent $PSScriptRoot
Set-Location $root

$backendPort = 10974
$frontendPort = 10975

# 1. KILL ZOMBIES on both ports
foreach ($p in $backendPort, $frontendPort) {
    Get-NetTCPConnection -LocalPort $p -ErrorAction SilentlyContinue |
        ForEach-Object { Stop-Process -Id $_.OwningProcess -Force -ErrorAction SilentlyContinue }
}

Write-Host "[chitchat] Starting backend on port $backendPort..."
# 2. START BACKEND in hidden window
Start-Process -FilePath "uv" -ArgumentList "run", "chitchat", "--serve", "--port", "$backendPort" -WorkingDirectory $root -WindowStyle Hidden

# 3. WAIT for backend to be ready
Write-Host "[chitchat] Waiting for backend..."
$ready = $false
for ($i = 0; $i -lt 30; $i++) {
    try {
        $null = Invoke-WebRequest -Uri "http://127.0.0.1:$backendPort/api/health" -UseBasicParsing -TimeoutSec 2
        $ready = $true
        Write-Host "[chitchat] Backend ready."
        break
    } catch {
        Start-Sleep -Milliseconds 500
    }
}
if (-not $ready) {
    Write-Warning "[chitchat] Backend did not respond in 15s - continuing anyway."
}

# 4. ENSURE NODE_MODULES
Set-Location (Join-Path $root "web_sota")
if (-not (Test-Path "node_modules")) {
    Write-Host "[chitchat] Installing frontend dependencies..."
    npm install
}

# 5. OPEN BROWSER
Start-Process "http://127.0.0.1:$frontendPort/"

# 6. START FRONTEND in foreground
Write-Host "[chitchat] Starting frontend on port $frontendPort... (Ctrl+C to stop)"
npm run dev
