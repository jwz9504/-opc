from __future__ import annotations

from datetime import datetime
from typing import Any

from sqlalchemy import DateTime, String, Text, create_engine
from sqlalchemy.engine import Engine
from sqlalchemy.orm import DeclarativeBase, Mapped, Session, mapped_column, sessionmaker


class Base(DeclarativeBase):
    pass

class MeetingModel(Base):
    __tablename__ = "meetings_orm"
    meeting_id: Mapped[str] = mapped_column(String(64), primary_key=True)
    owner_id: Mapped[str] = mapped_column(String(255), nullable=False)
    question: Mapped[str] = mapped_column(Text, nullable=False)
    resume_token: Mapped[str] = mapped_column(String(128), nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, nullable=False)

class ArtifactModel(Base):
    __tablename__ = "artifacts_orm"
    artifact_id: Mapped[str] = mapped_column(String(255), primary_key=True)
    artifact_type: Mapped[str] = mapped_column(String(64), nullable=False)
    payload: Mapped[str] = mapped_column(Text, nullable=False)

class MeetingStateModel(Base):
    __tablename__ = "meeting_states_orm"
    meeting_id: Mapped[str] = mapped_column(String(64), primary_key=True)
    payload: Mapped[str] = mapped_column(Text, nullable=False)

class RequestKeyModel(Base):
    __tablename__ = "request_keys_orm"
    request_key: Mapped[str] = mapped_column(String(255), primary_key=True)
    meeting_id: Mapped[str] = mapped_column(String(64), nullable=False)

def create_engine_and_session(url: str = "sqlite:///data/meetings.db") -> tuple[Engine, sessionmaker[Session]]:
    connect_args: dict[str, Any] = {"check_same_thread": False} if url.startswith("sqlite") else{}
    engine = create_engine(url, connect_args=connect_args)
    Base.metadata.create_all(engine)
    return engine, sessionmaker(bind=engine, expire_on_commit=False)
