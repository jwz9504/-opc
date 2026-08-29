from pathlib import Path

from agent_meeting.services.orm import create_engine_and_session
from agent_meeting.services.sqlalchemy_repository import SQLAlchemyRepository
from agent_meeting.services.sqlalchemy_store import SQLAlchemyMeetingStore


def test_application_store_roundtrip(tmp_path: Path) -> None:
    path = tmp_path / "app.db"
    store = SQLAlchemyMeetingStore(path)
    store.save_meeting("m1", "u1", "question", "token", "request-1")
    model = store.get_meeting("m1")
    assert model is not None
    assert model.owner_id == "u1"
    store.close()


def test_repository_request_key(tmp_path: Path) -> None:
    engine, session_factory = create_engine_and_session(f"sqlite:///{(tmp_path / 'r.db').as_posix()}")
    with session_factory() as session:
        assert SQLAlchemyRepository(session).get_by_request("missing") is None
    engine.dispose()
