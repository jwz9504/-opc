from __future__ import annotations

from collections.abc import Iterable
from typing import TypeVar

from .schemas.artifacts import CritiqueResolutionEvent
from .state import MeetingState

T = TypeVar("T")

def merge_ids(left: Iterable[str], right: Iterable[str]) -> list[str]:
    return sorted(set(left) | set(right))

def append_artifacts(state: MeetingState, ids: Iterable[str]) -> MeetingState:
    return state.model_copy(update={"artifact_ids": merge_ids(state.artifact_ids, ids)})

def set_active(state: MeetingState, kind: str, artifact_id: str) -> MeetingState:
    active = dict(state.active_ids)
    active[kind] = artifact_id
    return state.model_copy(update={"active_ids": active})

def project_critique_events(events: Iterable[CritiqueResolutionEvent]) -> dict[str, str]:
    result: dict[str, str] = {}
    for event in sorted(events, key=lambda e: (e.created_at, e.event_id)):
        if event.action == "addressed": result[event.critique_id] = "addressed"
        elif event.action == "verified" and result.get(event.critique_id) == "addressed": result[event.critique_id] = "resolved"
        elif event.action in {"invalid", "duplicate", "not_applicable", "accepted_risk"}: result[event.critique_id] = event.action
        elif event.action == "reopened": result[event.critique_id] = "reopened"
    return result
