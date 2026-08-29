
from agent_meeting.services.orm import AuditModel, create_engine_and_session


def test_audit_model_roundtrip():
    engine, factory = create_engine_and_session("sqlite:///:memory:")
    with factory() as session:
        event = AuditModel(meeting_id="m1", actor_id="u1", action="run", details='{"phase":"intake"}')
        session.add(event)
        session.commit()
        loaded = session.get(AuditModel, event.event_id)
        assert loaded is not None
        assert loaded.action == "run"
    engine.dispose()
