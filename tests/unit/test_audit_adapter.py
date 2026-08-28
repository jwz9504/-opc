from agent_meeting.services.audit_adapter import AuditAdapter


class Sink:
    def __init__(self):
        self.events = []

    def append(self, meeting_id, actor_id, action, details=None):
        self.events.append((meeting_id, actor_id, action, details))
        return self.events[-1]


def test_audit_adapter_records_structured_details():
    sink = Sink()
    AuditAdapter(sink).record("m1", "u1", "run", phase="research")
    assert sink.events == [("m1", "u1", "run", {"phase": "research"})]
