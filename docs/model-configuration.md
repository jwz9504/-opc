# 模型配置说明

默认模型是 Stub，不需要网络或 API Key：

```powershell
$env:AGENT_MEETING_MODEL_PROVIDER="stub"
$env:AGENT_MEETING_MODEL_ID="stub-v1"
```

模型配置通过环境变量读取：

```text
AGENT_MEETING_MODEL_PROVIDER
AGENT_MEETING_MODEL_ID
MODEL_API_KEY
```

当前 `ModelRegistry` 已支持按角色注册模型配置，并对结构化输出进行有限次数校验重试。真实供应商适配应实现为独立 Provider，不修改治理规则和 Graph 路由。
