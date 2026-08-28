from __future__ import annotations

import sqlite3
from pathlib import Path

from ..state import MeetingState


class SQLiteRepository:
    def __init__(self, path: str | Path = "data/meetings.db") -> None:
        self.path = Path(path)
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self.db = sqlite3.connect(self.path, check_same_thread=False)
        self.db.execute("CREATE TABLE IF NOT EXISTS meetings (meeting_id TEXT PRIMARY KEY, owner_id TEXT NOT NULL, question TEXT NOT NULL, resume_token TEXT NOT NULL)")
        self.db.execute("CREATE TABLE IF NOT EXISTS request_keys (request_key TEXT PRIMARY KEY, meeting_id TEXT NOT NULL)")
        self.db.execute("CREATE TABLE IF NOT EXISTS meeting_states (meeting_id TEXT PRIMARY KEY, payload TEXT NOT NULL)")
        self.db.commit()

    def save_meeting(self, meeting_id: str, owner_id: str, question: str, resume_token: str, request_key: str) -> None:
        with self.db:
            self.db.execute("INSERT OR IGNORE INTO meetings VALUES (?, ?, ?, ?)", (meeting_id, owner_id, question, resume_token))
            self.db.execute("INSERT OR IGNORE INTO request_keys VALUES (?, ?)", (request_key, meeting_id))

    def get_meeting(self, meeting_id: str) -> tuple[str, str, str, str] | None:
        row = self.db.execute("SELECT meeting_id, owner_id, question, resume_token FROM meetings WHERE meeting_id=?", (meeting_id,)).fetchone()
        return tuple(row) if row else None

    def get_by_request(self, request_key: str) -> str | None:
        row = self.db.execute("SELECT meeting_id FROM request_keys WHERE request_key=?", (request_key,)).fetchone()
        return row[0] if row else None

    def save_state(self, state: MeetingState) -> None:
        with self.db:
            self.db.execute("INSERT OR REPLACE INTO meeting_states VALUES (?, ?)", (state.thread_id, state.model_dump_json()))

    def load_state(self, meeting_id: str) -> MeetingState | None:
        row = self.db.execute("SELECT payload FROM meeting_states WHERE meeting_id=?", (meeting_id,)).fetchone()
        return MeetingState.model_validate_json(row[0]) if row else None
