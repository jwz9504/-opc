
## 任务计划程序自动托管

以管理员 PowerShell 执行：

```powershell
.\scripts\manage-windows-task.ps1 -Action install
.\scripts\manage-windows-task.ps1 -Action status
.\scripts\manage-windows-task.ps1 -Action uninstall
```

脚本会在系统启动时运行服务，并配置失败自动重启。首次安装前请确认 `uv` 已安装且项目目录可访问。
