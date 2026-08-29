param(
    [int]$Port = 8000
)
$ErrorActionPreference = "Stop"
$root = Split-Path -Parent $PSScriptRoot
Set-Location $root
if (-not $env:AGENT_MEETING_API_TOKEN) { $env:AGENT_MEETING_API_TOKEN = "dev-token" }
& uv sync
& uv run uvicorn agent_meeting.api.app:app --host 127.0.0.1 --port $Port
