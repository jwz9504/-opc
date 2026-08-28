from __future__ import annotations

from collections.abc import Iterable

from ..schemas.artifacts import GateResult, SoftEvaluation
from .decision import aggregate_gates, aggregate_soft


def final_quality_decision(
    gates: Iterable[GateResult],
    required_gates: set[str],
    soft_evaluations: Iterable[SoftEvaluation],
    *,
    unresolved_critical: int = 0,
    human_approved: bool = False,
) -> str:
    gate_status = aggregate_gates(gates, required_gates)
    if gate_status == "reject":
        return "reject"
    if gate_status != "pass" or unresolved_critical:
        return "human_review"
    if aggregate_soft(soft_evaluations) is None:
        return "human_review"
    return "approve" if human_approved else "pending_human_approval"
