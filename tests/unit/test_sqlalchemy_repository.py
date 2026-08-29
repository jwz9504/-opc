from datetime import UTC, datetime

from agent_meeting.services.orm import MeetingModel, create_engine_and_session
from agent_meeting.services.sqlalchemy_repository import SQLAlchemyRepository


def test_sqlalchemy_repository_roundtrip():
    engine, session_factory = create_engine_and_session("sqlite:///:memory:")
    with session_factory() as session:
        repository = SQLAlchemyRepository(session)
        repository.save_meeting(MeetingModel(meeting_id="m1", owner_id="u1", question="q", resume_token="t", created_at=datetime.now(UTC)))
        assert repository.get_meeting("m1").question == "q"
        repository.save_artifact("m1:a", "test", {"ok": True})
        assert repository.get_artifact("m1:a").artifact_type == "test"
    engine.dispose()
