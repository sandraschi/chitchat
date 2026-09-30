Param([switch]$Headless)

# --- SOTA Headless Standard ---
if ($Headless -and ($Host.UI.RawUI.WindowTitle -notmatch 'Hidden')) {
    Start-Process pwsh -ArgumentList '-NoProfile', '-File', $PSCommandPath, '-Headless' -WindowStyle Hidden
    exit
}

$ErrorActionPreference = "Stop"
$WebPort = 10972
$HermesBin = "/home/sandr/.local/bin/hermes"

# 1. Ensure WSL2 is running
$wslCheck = wsl --list --running 2>&1
if ($wslCheck -notmatch 'Ubuntu') {
    Write-Host "[hermes] Starting WSL2..."
    wsl --distribution Ubuntu --exec echo "WSL2 ready" 2>&1 | Out-Null
}

# 2. Get WSL2 IP
$wslIp = (wsl bash -c "hostname -I | awk '{print `$1}'").Trim()
Write-Host "[hermes] WSL2 IP: $wslIp"

# 3. Stop any stale dashboard on the fleet port
wsl $HermesBin dashboard --stop 2>&1 | Out-Null

# 4. Start Hermes 0.15+ built-in dashboard in WSL2 background
Write-Host "[hermes] Starting Hermes dashboard on port $WebPort..."
wsl bash -c "nohup $HermesBin dashboard --port $WebPort --host 0.0.0.0 --no-open --insecure --skip-build > /tmp/hermes-dashboard.log 2>&1 &"

# 5. Wait for health endpoint
Write-Host "[hermes] Waiting for dashboard..."
$ready = $false
for ($i = 0; $i -lt 30; $i++) {
    try {
        $null = Invoke-WebRequest -Uri "http://${wslIp}:$WebPort/health" -UseBasicParsing -TimeoutSec 2
        $ready = $true
        Write-Host "[hermes] Dashboard ready."
        break
    } catch {
        Start-Sleep -Milliseconds 500
    }
}
if (-not $ready) {
    Write-Warning "[hermes] Dashboard did not respond in 15s - continuing anyway."
}

# 6. Open browser
if (-not $Headless) {
    Start-Process "http://${wslIp}:$WebPort/"
}

Write-Host "[hermes] Hermes dashboard: http://${wslIp}:$WebPort/"
Write-Host "[hermes] WSL2-based. Restart WSL2 and IP will change. Consider setting up netsh portproxy."
