from datetime import datetime
from typing import Any


class AuditEvent:
    event_id: str
    meeting_id: str
    actor_id: str
    action: str
    details: dict[str, Any]
    created_at: datetime
