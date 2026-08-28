# LangGraph Agents 会议与报告系统

当前实现从阶段 0–9 建设：可信 Schema/Reducer、治理规则、Stub 工作流、证据校验、恢复机制、模型适配、安全边界和 API 服务核心。默认使用 Stub，不访问真实模型或外部写接口。

## 本地运行

```bash
python -m venv .venv
# Windows
.venv\\Scripts\\activate
# Linux/macOS
source .venv/bin/activate
pip install -e ".[dev]"
pytest -q
ruff check .
mypy src
```

核心原则：所有 Artifact 绑定冻结治理版本；历史事件追加保存；硬门禁不可被软评分覆盖；最终发布需要人工批准。
