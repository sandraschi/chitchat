# Per-repo fleet start config for chitchat
# Edit ports/backend target here - start.ps1 is fleet-standard.
@{
    Name         = 'chitchat'
    BackendPort  = 10974
    FrontendPort = 10975
    HealthPath   = '/api/health'
    WebRoot      = 'web_sota'
    Backend = @{
        Kind          = 'uvicorn'
        UvicornTarget = 'chitchat.app:app'
        SyncExtras    = @('dev')
        Env           = @{ WEB_PORT = '10974' }
    }
    Frontend = @{
        Kind           = 'vite-npm'
        PackageManager = 'npm'
        PortEnvVar     = 'VITE_PORT'
        ApiTargetEnv   = 'VITE_API_TARGET'
    }
}
