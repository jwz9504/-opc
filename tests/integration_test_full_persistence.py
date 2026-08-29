from pathlib import Path

from agent_meeting.api.dto import MeetingCreate
from agent_meeting.api.service import MeetingService
from agent_meeting.services.sqlite_repository import SQLiteRepository


def test_report_and_artifacts_survive_service_recreation(tmp_path: Path) -> None:
    database = tmp_path / "full.db"
    first = MeetingService(SQLiteRepository(database))
    meeting = first.create(MeetingCreate(question="full", owner_id="u"), "full-1")
    first.run(meeting.meeting_id, "u")
    first.report(meeting.meeting_id, "u")
    second = MeetingService(SQLiteRepository(database))
    report = second.report(meeting.meeting_id, "u")
    assert report["meeting_id"] == meeting.meeting_id
    assert second.audit_events(meeting.meeting_id, "u")
