from __future__ import annotations

import sqlite3
from typing import Any

from .retrieval import RetrievalResult


class EvidenceRepository:
    def __init__(self, db: sqlite3.Connection) -> None:
        self.db = db
        self.db.execute("CREATE TABLE IF NOT EXISTS source_snapshots (snapshot_id TEXT PRIMARY KEY, uri TEXT NOT NULL, title TEXT NOT NULL, content TEXT NOT NULL, content_hash TEXT NOT NULL, retrieved_at TEXT NOT NULL)")
        self.db.commit()

    def save_results(self, meeting_id: str, results: list[RetrievalResult]) -> list[str]:
        ids: list[str] = []
        for index, result in enumerate(results, 1):
            snapshot_id = f"{meeting_id}:snapshot:{index}"
            self.db.execute("INSERT OR REPLACE INTO source_snapshots VALUES (?, ?, ?, ?, ?, ?)", (snapshot_id, result.uri, result.title, result.content, result.content_hash, result.retrieved_at.isoformat()))
            ids.append(snapshot_id)
        self.db.commit()
        return ids

    def list_for_meeting(self, meeting_id: str) -> list[dict[str, Any]]:
        rows = self.db.execute("SELECT snapshot_id, uri, title, content_hash, retrieved_at FROM source_snapshots WHERE snapshot_id LIKE ? ORDER BY snapshot_id", (f"{meeting_id}:%",)).fetchall()
        return [{"snapshot_id": row[0], "uri": row[1], "title": row[2], "content_hash": row[3], "retrieved_at": row[4]} for row in rows]
