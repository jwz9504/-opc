from __future__ import annotations

import json
import sqlite3
from typing import Any


class AuditRepository:
    def __init__(self, db: sqlite3.Connection) -> None:
        self.db = db
        self.db.execute(
            """CREATE TABLE IF NOT EXISTS audit_events (
                event_id INTEGER PRIMARY KEY AUTOINCREMENT,
                meeting_id TEXT NOT NULL,
                actor_id TEXT NOT NULL,
                action TEXT NOT NULL,
                details TEXT NOT NULL,
                created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
            )"""
        )
        self.db.commit()

    def append(
        self,
        meeting_id: str,
        actor_id: str,
        action: str,
        details: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        payload = json.dumps(details or{} , ensure_ascii=False, sort_keys=True)
        cursor = self.db.execute(
            "INSERT INTO audit_events (meeting_id, actor_id, action, details) VALUES (?, ?, ?, ?)",
            (meeting_id, actor_id, action, payload),
        )
        self.db.commit()
        return {
            "event_id": cursor.lastrowid,
            "meeting_id": meeting_id,
            "actor_id": actor_id,
            "action": action,
            "details": details or{}
        }

    def for_meeting(self, meeting_id: str) -> list[dict[str, Any]]:
        rows = self.db.execute(
            "SELECT event_id, meeting_id, actor_id, action, details, created_at "
            "FROM audit_events WHERE meeting_id=? ORDER BY event_id",
            (meeting_id,),
        ).fetchall()
        return [
            {
                "event_id": row[0],
                "meeting_id": row[1],
                "actor_id": row[2],
                "action": row[3],
                "details": json.loads(row[4]),
                "created_at": row[5],
            }
            for row in rows
        ]
