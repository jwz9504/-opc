from __future__ import annotations

from collections.abc import Iterable

from ..schemas.artifacts import GateResult, Proposal, SoftEvaluation


def authorize_critique_event(action: str, actor_role: str, author_role: str | None = None) -> None:
    if action == "accepted_risk" and actor_role != "human_owner":
        raise PermissionError("only human_owner may accept risk")
    if action == "verified" and author_role == actor_role:
        raise PermissionError("author cannot verify own critique")
    if action == "resolved":
        raise PermissionError("resolved is projected, not directly submitted")


def shortlist(proposals: Iterable[Proposal], limit: int = 5) -> list[Proposal]:
    eligible = [p for p in proposals if p.status == "eligible"]
    return eligible[:limit]


def aggregate_gates(gates: Iterable[GateResult], required: set[str]) -> str:
    values = {g.gate: g.result for g in gates}
    if any(values.get(name) == "fail" for name in required):
        return "reject"
    if any(values.get(name) != "pass" for name in required):
        return "human_review"
    return "pass"


def aggregate_soft(evaluations: Iterable[SoftEvaluation]) -> float | None:
    scores = {"poor": 1, "acceptable": 2, "good": 3, "excellent": 4}
    values = [scores[e.result] for e in evaluations if e.result != "abstain"]
    return sum(values) / len(values) if values else None


def can_freeze(*, gate_status: str, unresolved_critical: int, human_approved: bool) -> bool:
    return gate_status == "pass" and unresolved_critical == 0 and human_approved
