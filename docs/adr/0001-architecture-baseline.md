# ADR-0001: Architecture baseline

- 阶段化状态机替代自由群聊。
- Scope、Agenda、Evaluation Policy 经人工确认后冻结。
- Artifact 绑定治理版本，历史 Revision/Decision/Critique Event 追加保存。
- Grounding、硬门禁、回归和最终人工批准由代码约束。
- Checkpoint、Operation Ledger、Outbox、Branch Task 分离；阶段 0–2 不执行真实外部写入。
