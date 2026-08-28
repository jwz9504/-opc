from __future__ import annotations

from collections import Counter
from collections.abc import Iterable
from typing import Literal

from ..schemas.artifacts import (
    ArtifactEnvelope,
    DecisionRecord,
    Proposal,
    ProposalComparison,
    ProposalDisposition,
)

Disposition = Literal["eligible", "ineligible", "shortlisted", "selected", "pareto_candidate", "rejected"]


def classify_comparisons(comparisons: Iterable[ProposalComparison]) -> dict[str, set[str]]:
    wins: Counter[str] = Counter()
    losses: Counter[str] = Counter()
    ties: set[str] = set()
    depends: set[str] = set()
    for comparison in comparisons:
        if comparison.outcome == "a_preferred":
            wins[comparison.proposal_a_id] += 1
            losses[comparison.proposal_b_id] += 1
        elif comparison.outcome == "b_preferred":
            wins[comparison.proposal_b_id] += 1
            losses[comparison.proposal_a_id] += 1
        elif comparison.outcome == "tie":
            ties.update((comparison.proposal_a_id, comparison.proposal_b_id))
        else:
            depends.update((comparison.proposal_a_id, comparison.proposal_b_id))
    return {"wins": set(wins), "losses": set(losses), "ties": ties, "depends": depends}


def disposition_from_comparisons(
    proposals: Iterable[Proposal], comparisons: Iterable[ProposalComparison]
) -> list[ProposalDisposition]:
    proposals = list(proposals)
    groups = classify_comparisons(comparisons)
    dispositions = []
    for proposal in proposals:
        identifier = proposal.envelope.artifact_id
        if identifier in groups["depends"] or identifier in groups["ties"]:
            kind: Disposition = "pareto_candidate"
            reasons = ["comparison_requires_human_judgment"]
        elif identifier in groups["wins"] and identifier not in groups["losses"]:
            kind = "selected"
            reasons = ["dominates_pairwise_comparisons"]
        else:
            kind = "rejected"
            reasons = ["not_preferred_in_pairwise_comparisons"]
        dispositions.append(ProposalDisposition(envelope=proposal.envelope, proposal_id=identifier, disposition=kind, reasons=reasons))
    return dispositions


def build_decision_record(
    envelope: ArtifactEnvelope,
    dispositions: Iterable[ProposalDisposition],
    rationale: str,
    selected_id: str | None = None,
) -> DecisionRecord:
    items = list(dispositions)
    rejected = [item.proposal_id for item in items if item.disposition == "rejected"]
    return DecisionRecord(envelope=envelope, selected_proposal_id=selected_id, rationale=rationale, rejected_proposal_ids=rejected)
