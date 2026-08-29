from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from .orm import create_engine_and_session
from .sqlalchemy_repository import SQLAlchemyRepository


class SQLAlchemyArtifactStore:
    def __init__(self, database: str | Path = "data/meetings.db") -> None:
        self.engine, self.session_factory = create_engine_and_session(f"sqlite:///{Path(database).as_posix()}")

    def save(self, artifact_id: str, artifact_type: str, payload: dict[str, Any]) -> None:
        with self.session_factory() as session:
            SQLAlchemyRepository(session).save_artifact(artifact_id, artifact_type, payload)

    def get(self, artifact_id: str) -> dict[str, Any] | None:
        with self.session_factory() as session:
            model = SQLAlchemyRepository(session).get_artifact(artifact_id)
            if model is None:
                return None
            return {"artifact_id": model.artifact_id, "artifact_type": model.artifact_type, "payload": json.loads(model.payload)}

    def all_artifacts(self) -> list[dict[str, Any]]:
        with self.session_factory() as session:
            return [{"artifact_id": model.artifact_id, "artifact_type": model.artifact_type, "payload": json.loads(model.payload)} for model in SQLAlchemyRepository(session).list_artifacts()]

    def list_for_meeting(self, meeting_id: str) -> list[dict[str, Any]]:
        items: list[dict[str, Any]] = self.all_artifacts()
        return [item for item in items if meeting_id in str(item["artifact_id"])]

    def close(self) -> None:
        self.engine.dispose()
