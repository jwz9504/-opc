# Windows 原生验收故障排查

## 8000 或 8765 端口被占用

查询端口：

```powershell
Get-NetTCPConnection -LocalPort 8000,8765 -State Listen
```

查看进程：

```powershell
Get-Process -Id <PID>
```

仅当确认是本项目遗留进程时再停止：

```powershell
Stop-Process -Id <PID> -Force
```

启动脚本会自动识别项目自身的 Python/Uvicorn 进程，重复启动时直接复用；若端口被其他进程占用则明确失败。

## 一键黑盒验收

```powershell
uv run python scripts/windows_blackbox_restart.py
```

脚本使用用户目录下的显式 `uv.exe` 路径，避免任务计划程序或非交互环境找不到 `uv`。
