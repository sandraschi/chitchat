# Sets up netsh portproxy to forward localhost:10972 → WSL2 VM
# Run once after WSL2 reboot (IP changes). Run as Administrator.
Param()

$WebPort = 10972
$wslIp = (wsl bash -c "hostname -I | awk '{print `$1}'").Trim()

Write-Host "Setting up portproxy: localhost:$WebPort → $wslIp`:$WebPort"

# Remove any existing rule on this port
netsh interface portproxy delete v4tov4 listenport=$WebPort 2>$null

# Add new rule
netsh interface portproxy add v4tov4 listenport=$WebPort listenaddress=0.0.0.0 connectport=$WebPort connectaddress=$wslIp

# Show the rule
netsh interface portproxy show v4tov4 | Select-String $WebPort

Write-Host ""
Write-Host "Done. Now access http://localhost:$WebPort/ from Windows."
Write-Host "Run this script again after WSL2 restarts (IP changes)."
