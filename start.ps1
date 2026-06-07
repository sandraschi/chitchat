Param([switch]$Headless)

# Root-level launcher - delegates to web_sota/start.ps1
& (Join-Path $PSScriptRoot "web_sota\start.ps1") @PSBoundParameters
