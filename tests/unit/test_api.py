from agent_meeting.api.dto import MeetingCreate
from agent_meeting.api.service import MeetingService
from agent_meeting.services.report_renderer import render_json, render_markdown


def test_meeting_service_authorization_and_idempotency():
    service = MeetingService()
    payload = MeetingCreate(question="研究问题", owner_id="owner")
    first = service.create(payload, "req-1")
    second = service.create(payload, "req-1")
    assert first.meeting_id == second.meeting_id
    try:
        service.run(first.meeting_id, "other")
        raise AssertionError("expected authorization failure")
    except PermissionError:
        pass


def test_report_renderers_have_fixed_sections():
    output = render_markdown({"title": "测试", "执行摘要": "摘要"})
    assert "## 决策记录" in output
    assert '"执行摘要"' in render_json({"执行摘要": "摘要"})
