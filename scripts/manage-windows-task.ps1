param(
    [ValidateSet("install", "uninstall", "status")]
    [string]$Action = "install",
    [string]$TaskName = "Agent Meeting API",
    [int]$Port = 8000
)
$ErrorActionPreference = "Stop"
$root = Split-Path -Parent $PSScriptRoot
$startScript = Join-Path $PSScriptRoot "start-windows.ps1"

switch ($Action) {
    "install" {
        $taskAction = New-ScheduledTaskAction -Execute "powershell.exe" -Argument "-NoProfile -ExecutionPolicy Bypass -File `"$startScript`" -Port $Port" -WorkingDirectory $root
        $trigger = New-ScheduledTaskTrigger -AtStartup
        $settings = New-ScheduledTaskSettingsSet -RestartCount 3 -RestartInterval (New-TimeSpan -Minutes 1)
        Register-ScheduledTask -TaskName $TaskName -Action $taskAction -Trigger $trigger -Settings $settings -RunLevel Highest -Force | Out-Null
        Write-Host "Installed scheduled task: $TaskName"
    }
    "uninstall" {
        Unregister-ScheduledTask -TaskName $TaskName -Confirm:$false
        Write-Host "Removed scheduled task: $TaskName"
    }
    "status" {
        Get-ScheduledTask -TaskName $TaskName | Select-Object TaskName, State, TaskPath
    }
}
