# Agent Meeting 项目交接手册

> 面向下一位负责继续开发、部署和维护本项目的工程师。
>
> 文档日期：2026-08-29
> 当前分支：`main`
> 当前远程仓库：<https://github.com/jwz9504/-opc>

---

## 1. 项目目标

这是一个面向研究和决策问题的治理型多 Agent 会议系统。系统不是自由群聊，而是由固定治理规则约束的阶段化工作流：

```text
问题输入
→ 治理版本确认
→ 研究与创意
→ Proposal 比较和选择
→ Revision/Critique
→ Grounding/专业门禁
→ 人工最终批准
→ 报告和审计
```

核心设计原则：

- Agent 通过结构化 Artifact 协作，而不是依赖自由文本；
- Scope、Agenda、Evaluation Policy 必须经过人工确认并冻结；
- 硬门禁失败不能被软评分覆盖；
- Critique 必须经过独立验证；
- Grounding 必须能追溯到 Claim、Evidence 和 Source Snapshot；
- 历史产物追加保存，不直接覆盖；
- 外部副作用必须经过审批和幂等控制；
- 最终报告必须人工批准。

---

## 2. 当前真实状态

当前项目是一个**Windows 原生、可启动、可持久化的 Stub MVP**，不是生产级多租户系统。

### 已具备

- FastAPI + Uvicorn HTTP 服务；
- `uv` 依赖管理；
- SQLite 业务数据库；
- SQLAlchemy ORM 和 Alembic 基线；
- LangGraph `StateGraph`；
- LangGraph SQLite Checkpoint；
- `interrupt` / `Command(resume=...)`；
- 会议、状态、Artifact、报告、审计持久化基础；
- Proposal 生成和人工选择；
- Stub Model；
- Stub Retrieval Provider；
- Source Snapshot 内容哈希；
- API Token 鉴权；
- Windows 启动脚本；
- Windows Task Scheduler / WinSW 配置示例；
- 进程杀死、重启、恢复黑盒验收脚本；
- SQLite 备份和完整性检查脚本。

### 尚未达到生产级的部分

- 真实模型 Provider 尚未接入主流程；
- 真实检索服务尚未接入；
- Graph 仍是简化的 `governance → work → final` 结构；
- Critique、ReworkPlan、Candidate Revision、Grounding、Hard Gate 目前部分是 Stub 状态；
- SQLAlchemy 已有完整适配层，但旧 `sqlite3` Repository 兼容路径仍存在；
- 正式 JWT/OIDC 尚未接入；
- 没有前端界面；
- 没有 PostgreSQL、S3、Kubernetes 或 Docker 部署；
- 没有完整的生产监控、告警和灾备体系。

不要把当前版本描述成“完整生产系统”。准确描述应为：

```text
Windows 原生单机可运行的治理型会议 Stub MVP
```

---

## 3. 环境要求

推荐环境：

```text
Windows 10/11 或 Windows Server
Python 3.11+
uv
Git
Clash Verge（如果 GitHub 访问需要代理）
```

当前机器上已验证的工具路径：

```text
Python: C:\Program Files\Python311\python.exe
uv: C:\Users\Administrator\.local\bin\uv.exe
Git: C:\Program Files\Git\cmd\git.exe
```

如果终端找不到 `git` 或 `uv`，不要立即修改项目；先使用绝对路径检查：

```powershell
& "C:\Program Files\Git\cmd\git.exe" --version
& "$env:USERPROFILE\.local\bin\uv.exe" --version
```

---

## 4. 项目目录

```text
.
├── .env.example
├── .gitignore
├── README.md
├── pyproject.toml
├── uv.lock
├── alembic.ini
├── alembic/
│   ├── env.py
│   └── versions/
│       ├── 0001_orm_baseline.py
│       ├── 0002_extend_orm.py
│       └── 0003_report_audit.py
├── docs/
│   ├── adr/
│   ├── acceptance/
│   ├── model-configuration.md
│   ├── windows-native-runbook.md
│   ├── windows-task-scheduler.md
│   ├── windows-blackbox-troubleshooting.md
│   └── 本交接手册.md
├── scripts/
│   ├── start-windows.ps1
│   ├── manage-windows-task.ps1
│   ├── windows_blackbox_restart.py
│   ├── sqlalchemy_restart_check.py
│   ├── backup-sqlite.py
│   └── check-sqlite.py
├── src/agent_meeting/
│   ├── api/
│   ├── nodes/
│   ├── policies/
│   ├── schemas/
│   ├── security/
│   ├── services/
│   ├── graph.py
│   ├── langgraph_workflow.py
│   ├── reducers.py
│   ├── state.py
│   └── config.py
└── tests/
```

---

## 5. 依赖和安装

项目使用 `uv`，不要直接以全局 `pip` 作为长期依赖管理方式。

首次安装：

```powershell
cd C:\Users\Administrator\.zcode\workspace\default
uv sync
```

开发依赖包括：

- Pydantic；
- FastAPI；
- Uvicorn；
- LangGraph；
- LangGraph SQLite Checkpoint；
- SQLAlchemy；
- Alembic；
- pytest；
- pytest-cov；
- Ruff；
- Mypy；
- HTTPX。

锁文件是：

```text
uv.lock
```

修改 `pyproject.toml` 后应执行：

```powershell
uv lock
uv sync
```

---

## 6. 配置

复制配置示例：

```powershell
Copy-Item .env.example .env
```

开发环境：

```powershell
$env:AGENT_MEETING_ENV="dev"
$env:AGENT_MEETING_API_TOKEN="dev-token"
$env:AGENT_MEETING_MODEL_PROVIDER="stub"
$env:AGENT_MEETING_MODEL_ID="stub-v1"
```

可配置路径：

```text
AGENT_MEETING_DATABASE       默认 data/meetings.db
AGENT_MEETING_ARTIFACT_DIR   默认 data/artifacts
AGENT_MEETING_REPORT_DIR     默认 data/reports
AGENT_MEETING_API_TOKEN      默认 dev-token（仅开发环境）
AGENT_MEETING_ENV             默认 dev
AGENT_MEETING_MODEL_PROVIDER  默认 stub
AGENT_MEETING_MODEL_ID        默认 stub-v1
MODEL_API_KEY                 当前 Stub 不需要
```

生产环境必须配置非默认 Token：

```powershell
$env:AGENT_MEETING_ENV="prod"
$env:AGENT_MEETING_API_TOKEN="替换为足够长度的随机字符串"
```

生产环境使用 `dev-token` 会被配置模块拒绝。

---

## 7. 启动服务

### 7.1 推荐启动方式

```powershell
cd C:\Users\Administrator\.zcode\workspace\default
$env:AGENT_MEETING_API_TOKEN="dev-token"
uv sync
uv run alembic upgrade head
uv run uvicorn agent_meeting.api.app:app --host 127.0.0.1 --port 8000
```

API 文档：

<http://127.0.0.1:8000/docs>

健康检查：

```powershell
Invoke-RestMethod http://127.0.0.1:8000/health
Invoke-RestMethod http://127.0.0.1:8000/health/details
```

### 7.2 使用启动脚本

```powershell
powershell -NoProfile -ExecutionPolicy Bypass `
  -File .\scripts\start-windows.ps1 -Port 8000
```

启动脚本会：

1. 切换到项目根目录；
2. 检查 8000 端口；
3. 如果已有本项目 Python/Uvicorn 服务，则直接返回；
4. 如果端口被其他进程占用，则报错；
5. 执行 `uv sync`；
6. 执行 `uv run alembic upgrade head`；
7. 启动 Uvicorn。

查看端口：

```powershell
Get-NetTCPConnection -LocalPort 8000 -State Listen
```

停止已知服务：

```powershell
Stop-Process -Id <PID> -Force
```

只在确认该 PID 是本项目遗留进程时停止，不要误杀其他服务。

---

## 8. API 调用示例

所有接口默认需要：

```text
Authorization: Bearer dev-token
```

创建会议：

```powershell
$headers = @{
  Authorization = "Bearer dev-token"
  "X-Request-ID" = "demo-001"
}
$body = @{
  question = "评估是否建设内部知识库"
  owner_id = "jwz9504"
} | ConvertTo-Json

Invoke-RestMethod `
  -Uri http://127.0.0.1:8000/meetings `
  -Method Post `
  -Headers $headers `
  -ContentType "application/json" `
  -Body $body
```

启动会议：

```powershell
Invoke-RestMethod `
  -Uri "http://127.0.0.1:8000/meetings/{meeting_id}/run?actor_id=jwz9504" `
  -Method Post `
  -Headers @{ Authorization = "Bearer dev-token" }
```

查询会议：

```powershell
Invoke-RestMethod `
  -Uri "http://127.0.0.1:8000/meetings/{meeting_id}?actor_id=jwz9504" `
  -Headers @{ Authorization = "Bearer dev-token" }
```

查询 Artifact：

```powershell
Invoke-RestMethod `
  -Uri "http://127.0.0.1:8000/meetings/{meeting_id}/artifacts?actor_id=jwz9504&limit=20&offset=0" `
  -Headers @{ Authorization = "Bearer dev-token" }
```

按类型查询 Proposal：

```text
GET /meetings/{id}/artifacts?actor_id=jwz9504&artifact_type=proposal
```

查询报告：

```text
GET /meetings/{id}/report?actor_id=jwz9504
GET /meetings/{id}/report.json?actor_id=jwz9504
GET /meetings/{id}/report.md?actor_id=jwz9504
```

查询审计：

```text
GET /meetings/{id}/audit?actor_id=jwz9504
```

选择 Proposal：

```powershell
$body = @{
  actor_id = "jwz9504"
  proposal_id = "替换为候选 Proposal ID"
  rationale = "选择理由"
} | ConvertTo-Json

Invoke-RestMethod `
  -Uri "http://127.0.0.1:8000/meetings/{meeting_id}/select" `
  -Method Post `
  -Headers @{ Authorization = "Bearer dev-token" } `
  -ContentType "application/json" `
  -Body $body
```

恢复人工节点：

```text
POST /meetings/{id}/resume
```

请求体：

```json
{
  "decision": "confirm",
  "actor_id": "jwz9504",
  "token": "会议对应 resume token"
}
```

最终批准：

```json
{
  "decision": "approve",
  "actor_id": "jwz9504",
  "token": "会议对应 resume token"
}
```

取消会议：

```text
POST /meetings/{id}/cancel?actor_id=jwz9504
```

---

## 9. 工作流和状态

### 9.1 主要 LangGraph 节点

当前实现位于：

```text
src/agent_meeting/langgraph_workflow.py
```

当前图结构：

```text
START
→ governance
→ work
→ final
→ END
```

`governance`：

- 治理未确认时调用 `interrupt`；
- `confirm` 后继续；
- `cancel` 后进入 cancelled。

`work`：

- 生成 Stub 研究索引；
- 生成 3 个 Proposal；
- 写入 Decision pending 状态；
- 写入 Critique/Grounding/Gate 基础状态；
- 进入最终审批前状态。

`final`：

- 调用最终审批 `interrupt`；
- `approve` 后进入 frozen_final；
- 其他结果进入 cancelled。

### 9.2 MeetingState

定义位于：

```text
src/agent_meeting/state.py
```

主要字段：

```text
thread_id
phase
round
artifact_ids
active_ids
indexes
summaries
human_pending
cancelled
```

### 9.3 Checkpoint

LangGraph Checkpoint 使用：

```text
langgraph.checkpoint.sqlite.SqliteSaver
```

连接由：

```text
src/agent_meeting/langgraph_workflow.py
```

中的 `build_sqlite_graph()` 创建。

会议业务 SQLite 和 LangGraph Checkpoint 当前使用同一数据库文件，但表和职责分离。

---

## 10. 持久化结构

### 10.1 当前 SQLite 表

旧兼容表：

```text
meetings
request_keys
meeting_states
artifacts
reports
source_snapshots
audit_events
```

SQLAlchemy ORM 表：

```text
meetings_orm
artifacts_orm
meeting_states_orm
request_keys_orm
reports_orm
audit_events_orm
```

LangGraph Checkpoint 表由 `SqliteSaver` 管理。

### 10.2 ORM 文件

```text
src/agent_meeting/services/orm.py
src/agent_meeting/services/sqlalchemy_repository.py
src/agent_meeting/services/sqlalchemy_store.py
src/agent_meeting/services/sqlalchemy_report_store.py
src/agent_meeting/services/sqlalchemy_audit_store.py
src/agent_meeting/services/sqlalchemy_artifact_store.py
```

### 10.3 Repository 注意事项

当前项目处于迁移中：

- Meeting 主路径已经使用 SQLAlchemyMeetingStore；
- Report 主路径已经使用 SQLAlchemyReportStore；
- Audit 主路径已经使用 SQLAlchemyAuditStore；
- Artifact 主路径已经使用 SQLAlchemyArtifactStore；
- 旧 `sqlite3` Repository 仍保留兼容逻辑；
- 不要直接删除旧 Repository，先完成数据迁移和全链路回归。

---

## 11. Alembic

配置：

```text
alembic.ini
alembic/env.py
```

迁移版本：

```text
0001_orm_baseline
0002_extend_orm
0003_report_audit
```

执行迁移：

```powershell
uv run alembic upgrade head
```

查看当前版本：

```powershell
uv run alembic current
```

迁移原则：

- 不要手动删除生产表；
- 新表和字段必须添加迁移；
- 迁移前先备份 `data/meetings.db`；
- SQLite 迁移后执行完整性检查；
- 迁移脚本必须有升级和降级路径。

---

## 12. Artifact 和证据链

Artifact 相关文件：

```text
src/agent_meeting/services/artifact_repository.py
src/agent_meeting/services/sqlalchemy_artifact_store.py
src/agent_meeting/services/artifact_events.py
src/agent_meeting/services/evidence_repository.py
```

当前已支持：

- 会议 Artifact；
- Research 索引；
- Proposal；
- Source Snapshot；
- 内容哈希；
- 按会议查询；
- 类型过滤；
- 分页。

证据追踪目标：

```text
sentence_id
→ claim_ids
→ evidence_ids
→ source_snapshot_id
```

当前 Stub Retrieval：

```text
src/agent_meeting/services/retrieval.py
```

默认不访问外部网络，内容会被包装为：

```text
<untrusted-data>...</untrusted-data>
```

---

## 13. 安全边界

安全代码：

```text
src/agent_meeting/security/boundary.py
```

当前措施：

- 环境变量 API Token；
- 生产环境禁止默认 Token；
- 会议所有者授权；
- resume token 校验；
- 角色级工具权限；
- 网页/检索内容作为不可信数据；
- API Key、Token、Authorization、Password 脱敏。

注意：当前 Token 认证仍然是开发级 Bearer Token，不是正式身份系统。生产前需要：

- JWT/OIDC；
- Token 轮换；
- 用户和角色表；
- 限流；
- 审计登录和授权失败；
- 安全 Header；
- CORS 策略。

---

## 14. 备份和恢复

SQLite 完整性检查：

```powershell
uv run python scripts/check-sqlite.py
```

备份：

```powershell
uv run python scripts/backup-sqlite.py
```

备份目录：

```text
data/backups/
```

至少备份：

```text
data/meetings.db
data/reports/
data/artifacts/
```

建议备份流程：

```text
停止服务
→ 执行完整性检查
→ 复制数据库
→ 复制 reports/artifacts
→ 记录备份时间和版本
→ 重新启动服务
→ 执行健康检查
```

恢复流程：

```text
停止服务
→ 保存当前损坏文件副本
→ 恢复 meetings.db
→ 恢复 reports/
→ 恢复 artifacts/
→ 执行 integrity_check
→ 执行 alembic current
→ 启动服务
→ 执行黑盒查询
```

---

## 15. Windows 进程托管

### 手工启动

```powershell
powershell -ExecutionPolicy Bypass -File .\scripts\start-windows.ps1
```

### 任务计划程序

安装：

```powershell
powershell -ExecutionPolicy Bypass `
  -File .\scripts\manage-windows-task.ps1 -Action install
```

查看：

```powershell
powershell -ExecutionPolicy Bypass `
  -File .\scripts\manage-windows-task.ps1 -Action status
```

卸载：

```powershell
powershell -ExecutionPolicy Bypass `
  -File .\scripts\manage-windows-task.ps1 -Action uninstall
```

任务计划程序建议：

- 使用服务账号；
- 设置项目根目录为工作目录；
- 设置失败自动重启；
- 把 API Token 放在系统环境变量；
- 不要把真实 Token 写入脚本或仓库；
- 日志输出到 `data/logs/`。

### WinSW

配置示例：

```text
winsw-agent-meeting.xml
```

使用前必须修改：

- `<workingdirectory>`；
- `<executable>`；
- `<arguments>`；
- `<logpath>`。

---

## 16. 黑盒验收

### 16.1 完整重启验收

```powershell
uv run python scripts/windows_blackbox_restart.py
```

脚本覆盖：

- 启动服务；
- 健康检查；
- 创建会议；
- 运行会议；
- 终止服务；
- 重启服务；
- 查询原会议；
- 错误 Token 验证；
- JSON 报告查询；
- Markdown 报告下载；
- 审计查询。

### 16.2 SQLAlchemy 重启检查

```powershell
uv run python scripts/sqlalchemy_restart_check.py
```

### 16.3 质量检查

```powershell
uv run pytest -q
uv run ruff check .
uv run mypy src
```

当前已验证结果：

```text
pytest：32 passed
Ruff：通过
Mypy：通过
```

### 16.4 端口冲突

测试服务使用：

```text
8765
8766
```

如果脚本异常退出后端口仍被占用：

```powershell
Get-NetTCPConnection -LocalPort 8765,8766 -State Listen
Get-Process -Id <PID>
Stop-Process -Id <PID> -Force
```

仅停止确认属于本项目的进程。

---

## 17. Git 操作

远程：

```text
https://github.com/jwz9504/-opc.git
```

Git 绝对路径：

```text
C:\Program Files\Git\cmd\git.exe
```

如果 GitHub 访问失败，而浏览器能访问，检查 Clash Verge 代理。当前曾验证可用端口：

```text
127.0.0.1:7897
```

配置示例：

```powershell
& "C:\Program Files\Git\cmd\git.exe" config --local http.proxy http://127.0.0.1:7897
& "C:\Program Files\Git\cmd\git.exe" config --local https.proxy http://127.0.0.1:7897
```

检查：

```powershell
& "C:\Program Files\Git\cmd\git.exe" remote -v
& "C:\Program Files\Git\cmd\git.exe" status
& "C:\Program Files\Git\cmd\git.exe" log --oneline --decorate -10
```

重要：

- 不要在未检查远程历史前使用 force push；
- 不要覆盖远程已有提交；
- 提交前运行测试；
- 不要提交 `.env`、数据库、备份、缓存和 Token；
- 当前 `.gitignore` 已排除常见生成文件，但提交前仍应检查 `git status`。

---

## 18. 已知问题和接手优先级

### P0：修复 API/Graph 状态一致性

当前 `MeetingState` 和 LangGraph Checkpoint 都被保存，但两者不是单一事务。接手后应：

1. 定义 Graph 状态到业务状态的唯一投影；
2. 节点完成后再写 MeetingState；
3. 中断时保存可恢复的阶段和 payload；
4. 重启后优先以 LangGraph Checkpoint 为准；
5. 添加节点前、中、后崩溃测试。

### P1：完整拆分 Graph 节点

目标：

```text
intake_parse
→ draft_governance
→ human_confirm_governance
→ research
→ ideate
→ normalize_proposals
→ filter_and_shortlist
→ compare_proposals
→ select_direction
→ build_revision
→ red_team_review
→ triage_critiques
→ create_rework_plan
→ apply_rework
→ validate_grounding
→ run_hard_gates
→ human_final_approval
→ freeze_and_render
```

### P1：完成 Artifact 生命周期

需要独立持久化并追加保存：

```text
Claim
Evidence
SourceSnapshot
Proposal
ProposalComparison
DecisionRecord
Critique
CritiqueResolutionEvent
ReworkPlan
ReportRevision
ReportStatement
GroundingFinding
GateResult
SoftEvaluation
HumanDecision
ActionItem
MinorityOpinion
AuditEvent
```

### P1：统一 Repository

完成：

```text
sqlite3 Repository
→ SQLAlchemy Repository
```

删除兼容路径前必须：

- 迁移旧数据；
- 对比读写结果；
- 做重启验收；
- 做备份和恢复演练。

### P2：完整报告

最终报告必须由结构化 Artifact 生成，不能使用固定占位字符串。固定章节：

1. 执行摘要；
2. 问题定义、范围和成功标准；
3. 背景事实、证据和未验证假设；
4. 候选方案及比较；
5. 推荐方案；
6. 实施步骤、资源和依赖；
7. 验收标准；
8. 风险、失败模式和缓解措施；
9. 决策记录；
10. 少数派意见；
11. 行动项与责任人；
12. 未决问题；
13. 证据与引用附录；
14. 会议审计摘要。

### P2：真实模型和检索

先实现独立 Provider 接口，再接真实供应商：

```text
Stub Model
→ 单个真实模型
→ 结构化输出校验
→ 有限重试/fallback
→ Golden Cases
→ 真实检索
```

---

## 19. 接手后第一周建议

### 第一天：确认基线

```powershell
uv sync
uv run pytest -q
uv run ruff check .
uv run mypy src
uv run alembic current
uv run python scripts/check-sqlite.py
```

### 第二天：完整黑盒

```powershell
uv run python scripts/windows_blackbox_restart.py
uv run python scripts/sqlalchemy_restart_check.py
```

### 第三天：读关键文件

按顺序阅读：

```text
README.md
docs/langgraph-agent-meeting-project-manual.md
docs/langgraph-agent-meeting-build-manual.md
docs/windows-native-runbook.md
src/agent_meeting/api/app.py
src/agent_meeting/api/service.py
src/agent_meeting/langgraph_workflow.py
src/agent_meeting/services/sqlalchemy_store.py
src/agent_meeting/services/sqlalchemy_report_store.py
src/agent_meeting/services/sqlalchemy_audit_store.py
```

### 第四至五天：先不要加功能

先做：

- 清理 `MeetingService`；
- 画出现有数据流；
- 标出两套 Repository 的调用点；
- 标出 Graph Checkpoint 和 MeetingState 的写入点；
- 创建独立重构分支；
- 为当前行为增加黑盒回归测试。

---

## 20. 当前验收结论

当前版本可以验收为：

```text
Windows 原生单机可运行 Stub MVP
```

验收依据：

- API 可启动；
- SQLite 可持久化；
- LangGraph 可中断和恢复；
- 报告可查询和下载；
- Artifact 可查询；
- 审计可查询；
- 进程可杀死和重启；
- 数据库可备份和完整性检查；
- 测试、Ruff、Mypy 通过。

不能验收为：

```text
生产级多租户系统
真实模型生产系统
完整业务闭环
高可用分布式服务
```

---

## 21. 交接摘要

如果只记住几件事：

1. 当前部署路线是 Windows 原生，不需要 Docker；
2. 启动使用 `uv run uvicorn`；
3. 数据库是 SQLite，启动前执行 Alembic；
4. Graph 使用 LangGraph SQLite Checkpoint；
5. 默认模型和检索都是 Stub；
6. API Token 来自 `AGENT_MEETING_API_TOKEN`；
7. 先运行测试和黑盒验收，再修改主流程；
8. 不要 force push，不要提交 `.env` 和数据库；
9. 当前最大技术债是 Graph 状态、MeetingState 和多套 Repository 的一致性；
10. 下一步应做受控重构，而不是继续无序增加接口。
