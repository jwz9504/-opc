# Windows 原生运行手册

本项目不依赖 Docker，目标运行环境为 Windows 原生单进程。

## 手工启动

在项目根目录执行：

```powershell
uv sync
$env:AGENT_MEETING_API_TOKEN="dev-token"
uv run uvicorn agent_meeting.api.app:app --host 127.0.0.1 --port 8000
```

API 文档：`http://127.0.0.1:8000/docs`
健康检查：

```powershell
Invoke-RestMethod http://127.0.0.1:8000/health
```

数据目录：

```text
data/meetings.db
data/reports/
```

## 重启黑盒验收

```powershell
uv run python scripts/windows_blackbox_restart.py
```

脚本会启动、创建会议、运行、杀死、重新启动并查询同一会议。

## 任务计划程序

创建任务时使用：

```text
程序：C:\path\to\uv.exe
参数：run uvicorn agent_meeting.api.app:app --host 127.0.0.1 --port 8000
起始位置：C:\path\to\project
```

建议设置：

- 使用服务账号运行；
- 设置失败后自动重新启动；
- 设置工作目录为项目根目录；
- 将 `AGENT_MEETING_API_TOKEN` 配置在系统环境变量；
- 日志输出重定向到 `data/logs/`。

## WinSW

WinSW XML 示例：

```xml
<service>
  <id>agent-meeting</id>
  <name>Agent Meeting API</name>
  <description>Governed agent meeting API</description>
  <workingdirectory>C:\path\to\project</workingdirectory>
  <executable>C:\path\to\uv.exe</executable>
  <arguments>run uvicorn agent_meeting.api.app:app --host 127.0.0.1 --port 8000</arguments>
  <logpath>C:\path\to\project\data\logs</logpath>
  <onfailure action="restart" delay="10 sec" />
</service>
```

## 备份

停止服务后复制：

```text
data/meetings.db
data/reports/
```

恢复时覆盖对应数据文件，再启动服务并运行健康检查。
