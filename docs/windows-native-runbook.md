
## 生产加固

生产环境必须设置非默认 API Token：

```powershell
$env:AGENT_MEETING_ENV="prod"
$env:AGENT_MEETING_API_TOKEN="replace-with-a-long-random-token"
```

健康详情：

```powershell
Invoke-RestMethod http://127.0.0.1:8000/health/details
```

数据库完整性检查：

```powershell
uv run python scripts/check-sqlite.py
```

数据库备份：

```powershell
uv run python scripts/backup-sqlite.py
```

生产环境禁止使用默认 `dev-token`。启动时配置模块会主动拒绝该配置。
