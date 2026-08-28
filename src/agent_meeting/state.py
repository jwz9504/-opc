from __future__ import annotations

from typing import Any

from pydantic import BaseModel, Field


class MeetingState(BaseModel):
    thread_id: str
    phase: str = "intake"
    round: int = 0
    artifact_ids: list[str] = Field(default_factory=list)
    active_ids: dict[str, str] = Field(default_factory=dict)
    indexes: dict[str, list[str]] = Field(default_factory=dict)
    summaries: dict[str, Any] = Field(default_factory=dict)
    human_pending: bool = False
    cancelled: bool = False
