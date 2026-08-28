## Stub Business Loop Acceptance

当前 Stub 工作流已将研究索引和三个 Proposal 写入 `MeetingState.summaries`，并通过治理确认恢复继续执行质量阶段。关键状态仍通过 SQLite 持久化。

验证命令：

```text
pytest -q
ruff check .
mypy src
```

当前限制：Proposal、Claim、Evidence 尚未拆分为独立 SQLite Artifact 表记录；现阶段以状态摘要保存，后续接入真实 Artifact Repository 时迁移。
