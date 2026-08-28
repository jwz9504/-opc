from __future__ import annotations

import json
import sqlite3
from typing import Any


class ArtifactRepository:
    def __init__(self, db: sqlite3.Connection) -> None:
        self.db = db
        self.db.execute("CREATE TABLE IF NOT EXISTS artifacts (artifact_id TEXT PRIMARY KEY, artifact_type TEXT NOT NULL, payload TEXT NOT NULL)")
        self.db.commit()

    def save(self, artifact_id: str, artifact_type: str, payload: dict[str, Any]) -> None:
        self.db.execute("INSERT OR REPLACE INTO artifacts VALUES (?, ?, ?)", (artifact_id, artifact_type, json.dumps(payload, ensure_ascii=False, sort_keys=True)))
        self.db.commit()

    def list_for_meeting(self, meeting_id: str) -> list[dict[str, Any]]:
        rows = self.db.execute("SELECT artifact_id, artifact_type, payload FROM artifacts WHERE artifact_id LIKE ? ORDER BY artifact_id", (f"%{meeting_id}%",)).fetchall()
        return [{"artifact_id": row[0], "artifact_type": row[1], "payload": json.loads(row[2])} for row in rows]
