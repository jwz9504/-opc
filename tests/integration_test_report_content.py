from pathlib import Path

from agent_meeting.api.dto import MeetingCreate
from agent_meeting.api.service import MeetingService
from agent_meeting.services.sqlite_repository import SQLiteRepository


def test_report_contains_persisted_proposals(tmp_path: Path) -> None:
    service = MeetingService(SQLiteRepository(tmp_path / "m.db"))
    meeting = service.create(MeetingCreate(question="q", owner_id="o"), "req-report")
    service.run(meeting.meeting_id, "o")
    report = service.report(meeting.meeting_id, "o")
    assert "暂无候选方案" in str(report["推荐方案"]) or "渐进式试点" in str(report["推荐方案"])
