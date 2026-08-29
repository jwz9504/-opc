from __future__ import annotations

import builtins
import json
from pathlib import Path
from typing import Any

from .orm import AuditModel, create_engine_and_session
from .sqlalchemy_repository import SQLAlchemyRepository


class SQLAlchemyAuditStore:
    def __init__(self, database: str | Path = "data/meetings.db") -> None:
        self.engine, self.session_factory = create_engine_and_session(
            f"sqlite:///{Path(database).as_posix()}"
        )

    def append(
        self,
        meeting_id: str,
        actor_id: str,
        action: str,
        details: dict[str, Any] | None = None,
    ) -> None:
        with self.session_factory() as session:
            SQLAlchemyRepository(session).append_audit(
                meeting_id, actor_id, action, details or{}
            )

    def list(self, meeting_id: str) -> builtins.list[dict[str, Any]]:
        with self.session_factory() as session:
            rows = (
                session.query(AuditModel)
                .filter(AuditModel.meeting_id == meeting_id)
                .order_by(AuditModel.event_id)
                .all()
            )
            return [
                {
                    "event_id": row.event_id,
                    "meeting_id": row.meeting_id,
                    "actor_id": row.actor_id,
                    "action": row.action,
                    "details": json.loads(row.details),
                }
                for row in rows
            ]

    def for_meeting(self, meeting_id: str) -> builtins.list[dict[str, Any]]:
        return self.list(meeting_id)

    def close(self) -> None:
        self.engine.dispose()
