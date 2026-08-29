from __future__ import annotations

import json
from typing import Any

from sqlalchemy import select
from sqlalchemy.orm import Session

from .orm import ArtifactModel, MeetingModel


class SQLAlchemyRepository:
    def __init__(self, session: Session) -> None:
        self.session = session

    def save_meeting(self, model: MeetingModel) -> None:
        self.session.merge(model)
        self.session.commit()

    def get_meeting(self, meeting_id: str) -> MeetingModel | None:
        return self.session.get(MeetingModel, meeting_id)

    def save_artifact(self, artifact_id: str, artifact_type: str, payload: dict[str, Any]) -> None:
        self.session.merge(ArtifactModel(artifact_id=artifact_id, artifact_type=artifact_type, payload=json.dumps(payload, ensure_ascii=False, sort_keys=True)))
        self.session.commit()

    def get_artifact(self, artifact_id: str) -> ArtifactModel | None:
        return self.session.get(ArtifactModel, artifact_id)

    def list_artifacts(self) -> list[ArtifactModel]:
        return list(self.session.scalars(select(ArtifactModel).order_by(ArtifactModel.artifact_id)))
