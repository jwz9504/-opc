
## Artifact 查询

查询指定会议的结构化产物：

```powershell
$headers = @{ Authorization = "Bearer dev-token" }
Invoke-RestMethod "http://127.0.0.1:8000/meetings/{meeting_id}/artifacts?actor_id={owner_id}" -Headers $headers
```

只有会议所有者可以查看 Artifact。结果包含会议 Artifact、研究结果和 Proposal。
