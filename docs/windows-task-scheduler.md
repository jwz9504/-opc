# Windows 原生任务计划程序部署

以管理员身份打开 PowerShell，进入任务计划程序，创建基本任务：

- 名称：Agent Meeting API
- 触发器：系统启动时或用户登录时
- 操作：启动程序
- 程序：`C:\Users\Administrator\.local\bin\uv.exe`
- 参数：`run uvicorn agent_meeting.api.app:app --host 127.0.0.1 --port 8000`
- 起始位置：`C:\Users\Administrator\.zcode\workspace\default`

在“条件”中取消“仅在使用交流电源时启动”，在“设置”中启用失败后自动重新启动。

启动前配置系统环境变量：

```powershell
[Environment]::SetEnvironmentVariable("AGENT_MEETING_API_TOKEN", "dev-token", "Machine")
```

验证：

```powershell
Invoke-RestMethod http://127.0.0.1:8000/health
```
