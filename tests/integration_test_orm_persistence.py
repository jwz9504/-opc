from __future__ import annotations

import sqlite3
from pathlib import Path

from agent_meeting.api.dto import MeetingCreate
from agent_meeting.api.service import MeetingService
from agent_meeting.services.sqlite_repository import SQLiteRepository


def test_report_survives_service_recreation(tmp_path: Path) -> None:
    path = tmp_path / "report.db"
    first = MeetingService(SQLiteRepository(path))
    meeting = first.create(MeetingCreate(question="q", owner_id="u"), "r")
    first.report(meeting.meeting_id, "u")
    second = MeetingService(SQLiteRepository(path))
    report = second.report(meeting.meeting_id, "u")
    assert report["meeting_id"] == meeting.meeting_id


def test_orm_tables_exist(tmp_path: Path) -> None:
    path = tmp_path / "schema.db"
    MeetingService(SQLiteRepository(path))
    with sqlite3.connect(path) as db:
        names = {row[0] for row in db.execute("SELECT name FROM sqlite_master WHERE type='table'")}
    assert "reports_orm" in names
    assert "audit_events_orm" in names
