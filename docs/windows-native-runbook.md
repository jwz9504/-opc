
Artifact API 支持分页和类型筛选：

```text
GET /meetings/{id}/artifacts?actor_id=owner&artifact_type=proposal&limit=20&offset=0
```

`limit` 最大为 100，`offset` 从 0 开始。只有会议所有者可以查询。
