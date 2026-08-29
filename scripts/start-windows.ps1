param(
    [int]$Port = 8000
)
$ErrorActionPreference = "Stop"
$root = Split-Path -Parent $PSScriptRoot
Set-Location $root
if (-not $env:AGENT_MEETING_API_TOKEN) { $env:AGENT_MEETING_API_TOKEN = "dev-token" }

$listener = Get-NetTCPConnection -LocalAddress 127.0.0.1 -LocalPort $Port -State Listen -ErrorAction SilentlyContinue
if ($listener) {
    $process = Get-Process -Id $listener.OwningProcess -ErrorAction SilentlyContinue
    if ($process.ProcessName -in @("python", "uv", "uvicorn")) {
        Write-Host "Agent Meeting API already running on port $Port (PID $($process.Id))."
        exit 0
    }
    throw "Port $Port is occupied by PID $($listener.OwningProcess)."
}

& uv sync
& uv run alembic upgrade head
& uv run uvicorn agent_meeting.api.app:app --host 127.0.0.1 --port $Port
