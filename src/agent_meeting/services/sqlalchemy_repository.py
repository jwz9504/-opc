from __future__ import annotations

import json
from typing import Any

from sqlalchemy import select
from sqlalchemy.orm import Session

from .orm import (
    ArtifactModel,
    AuditModel,
    MeetingModel,
    MeetingStateModel,
    ReportModel,
    RequestKeyModel,
)


class SQLAlchemyRepository:
    def __init__(self, session: Session) -> None:
        self.session = session

    def save_meeting(self, model: MeetingModel, request_key: str | None = None) -> None:
        self.session.merge(model)
        if request_key:
            self.session.merge(RequestKeyModel(request_key=request_key, meeting_id=model.meeting_id))
        self.session.commit()

    def get_meeting(self, meeting_id: str) -> MeetingModel | None:
        return self.session.get(MeetingModel, meeting_id)

    def get_by_request(self, request_key: str) -> str | None:
        model = self.session.get(RequestKeyModel, request_key)
        return model.meeting_id if model else None

    def save_state(self, meeting_id: str, payload: str) -> None:
        self.session.merge(MeetingStateModel(meeting_id=meeting_id, payload=payload))
        self.session.commit()

    def load_state(self, meeting_id: str) -> str | None:
        model = self.session.get(MeetingStateModel, meeting_id)
        return model.payload if model else None

    def save_artifact(self, artifact_id: str, artifact_type: str, payload: dict[str, Any]) -> None:
        self.session.merge(ArtifactModel(artifact_id=artifact_id, artifact_type=artifact_type, payload=json.dumps(payload, ensure_ascii=False, sort_keys=True)))
        self.session.commit()

    def get_artifact(self, artifact_id: str) -> ArtifactModel | None:
        return self.session.get(ArtifactModel, artifact_id)

    def save_report(self, meeting_id: str, payload: dict[str, Any], markdown_path: str) -> None:
        self.session.merge(ReportModel(meeting_id=meeting_id, payload=json.dumps(payload, ensure_ascii=False, sort_keys=True), markdown_path=markdown_path))
        self.session.commit()

    def get_report(self, meeting_id: str) -> ReportModel | None:
        return self.session.get(ReportModel, meeting_id)

    def append_audit(self, meeting_id: str, actor_id: str, action: str, details: dict[str, Any]) -> None:
        self.session.add(AuditModel(meeting_id=meeting_id, actor_id=actor_id, action=action, details=json.dumps(details, ensure_ascii=False, sort_keys=True)))
        self.session.commit()

    def list_artifacts(self) -> list[ArtifactModel]:
        return list(self.session.scalars(select(ArtifactModel).order_by(ArtifactModel.artifact_id)))
