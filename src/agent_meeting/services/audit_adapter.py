from __future__ import annotations

from typing import Any, Protocol


class AuditSink(Protocol):
    def append(self, meeting_id: str, actor_id: str, action: str, details: dict[str, Any] | None = None) -> Any:
        ...


class AuditAdapter:
    def __init__(self, sink: AuditSink) -> None:
        self.sink = sink

    def record(self, meeting_id: str, actor_id: str, action: str, **details: Any) -> Any:
        return self.sink.append(meeting_id, actor_id, action, details or None)
