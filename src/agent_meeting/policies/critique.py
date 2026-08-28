from __future__ import annotations

from collections.abc import Iterable

from ..schemas.artifacts import ArtifactEnvelope, Critique, CritiqueResolutionEvent, ReworkPlan


def triage_critique(critique: Critique, valid: bool = True) -> str:
    return "valid" if valid else "invalid"


def create_rework_plan(
    critique: Critique, envelope: ArtifactEnvelope, responsible_role: str = "editor"
) -> ReworkPlan:
    return ReworkPlan(
        envelope=envelope,
        target_critique_ids=[critique.envelope.artifact_id],
        target_sections=[critique.target_artifact_id],
        expected_improvements=[critique.recommendation],
        protected_dimensions=["decision_record", "evidence_chain"],
        responsible_role=responsible_role,
        acceptance_criteria=["critique independently verified"],
    )


def validate_resolution_authority(
    event: CritiqueResolutionEvent, *, author_role: str | None = None
) -> None:
    if event.action == "verified" and author_role and event.actor_role == author_role:
        raise PermissionError("critique author cannot verify own change")
    if event.action == "accepted_risk" and event.actor_role != "human_owner":
        raise PermissionError("only human owner may accept risk")


def critique_status(events: Iterable[CritiqueResolutionEvent]) -> dict[str, str]:
    from ..reducers import project_critique_events
    return project_critique_events(events)
