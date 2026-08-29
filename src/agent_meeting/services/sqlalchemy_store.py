from __future__ import annotations

from datetime import UTC, datetime
from pathlib import Path

from .orm import MeetingModel, create_engine_and_session
from .sqlalchemy_repository import SQLAlchemyRepository


class SQLAlchemyMeetingStore:
    """Application-facing store backed by the ORM repository."""

    def __init__(self, database: str | Path = "data/meetings.db") -> None:
        self.engine, self.session_factory = create_engine_and_session(f"sqlite:///{Path(database).as_posix()}")

    def save_meeting(self, meeting_id: str, owner_id: str, question: str, resume_token: str, request_key: str) -> None:
        with self.session_factory() as session:
            SQLAlchemyRepository(session).save_meeting(
                MeetingModel(
                    meeting_id=meeting_id,
                    owner_id=owner_id,
                    question=question,
                    resume_token=resume_token,
                    created_at=datetime.now(UTC),
                ),
                request_key,
            )

    def get_by_request(self, request_key: str) -> str | None:
        with self.session_factory() as session:
            return SQLAlchemyRepository(session).get_by_request(request_key)

    def get_meeting(self, meeting_id: str) -> MeetingModel | None:
        with self.session_factory() as session:
            model = SQLAlchemyRepository(session).get_meeting(meeting_id)
            if model is None:
                return None
            return MeetingModel(
                meeting_id=model.meeting_id,
                owner_id=model.owner_id,
                question=model.question,
                resume_token=model.resume_token,
                created_at=model.created_at,
            )

    def close(self) -> None:
        self.engine.dispose()
