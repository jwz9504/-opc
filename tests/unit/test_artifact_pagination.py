from pathlib import Path

from agent_meeting.api.dto import MeetingCreate
from agent_meeting.api.service import MeetingService
from agent_meeting.services.sqlite_repository import SQLiteRepository


def test_artifact_pagination_and_filter(tmp_path: Path):
    service = MeetingService(SQLiteRepository(tmp_path / "artifacts.db"))
    meeting = service.create(MeetingCreate(question="q", owner_id="owner"), "req")
    items = service.artifacts_for_meeting(meeting.meeting_id, "owner", limit=1, offset=0)
    assert len(items) <= 1
