from pathlib import Path

from agent_meeting.api.dto import MeetingCreate
from agent_meeting.api.service import MeetingService
from agent_meeting.services.sqlite_repository import SQLiteRepository


def test_report_includes_quality_sections(tmp_path: Path) -> None:
    service = MeetingService(SQLiteRepository(tmp_path / "quality.db"))
    meeting = service.create(MeetingCreate(question="quality", owner_id="owner"), "quality-1")
    service.run(meeting.meeting_id, "owner")
    report = service.report(meeting.meeting_id, "owner")
    assert "Grounding 校验" in report
    assert "专业门禁" in report
    assert "风险与缓解" in report
