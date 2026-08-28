from __future__ import annotations

from collections.abc import Callable, Iterable
from itertools import combinations
from typing import Literal

from ..schemas.artifacts import Proposal, ProposalComparison, ProposalDisposition


def normalize_proposal(proposal: Proposal) -> Proposal:
    return proposal.model_copy(update={
        "title": " ".join(proposal.title.split()).strip(),
        "rationale": " ".join(proposal.rationale.split()).strip(),
        "status": "normalized",
    })


def deduplicate_proposals(proposals: Iterable[Proposal]) -> list[Proposal]:
    result: list[Proposal] = []
    seen: set[tuple[str, str]] = set()
    for proposal in proposals:
        key = (proposal.title.casefold(), proposal.rationale.casefold())
        if key not in seen:
            seen.add(key)
            result.append(proposal)
        else:
            result[-1] = result[-1].model_copy(update={"provenance": sorted(set(result[-1].provenance + proposal.provenance))})
    return result


def filter_proposals(proposals: Iterable[Proposal], forbidden_constraints: set[str]) -> list[ProposalDisposition]:
    output = []
    for proposal in proposals:
        violated = sorted(set(proposal.constraint_ids) & forbidden_constraints)
        disposition: Literal["eligible", "ineligible"] = "ineligible" if violated else "eligible"
        output.append(ProposalDisposition(
            envelope=proposal.envelope,
            proposal_id=proposal.envelope.artifact_id,
            disposition=disposition,
            reasons=[f"constraint:{item}" for item in violated],
        ))
    return output


def shortlist(proposals: Iterable[Proposal], limit: int = 5) -> list[Proposal]:
    eligible = [p.model_copy(update={"status": "eligible"}) for p in proposals if p.status in {"eligible", "normalized"}]
    return [p.model_copy(update={"status": "shortlisted"}) for p in eligible[:limit]]


def pairwise_comparisons(
    proposals: Iterable[Proposal],
    comparison_factory: Callable[[Proposal, Proposal], ProposalComparison],
) -> list[ProposalComparison]:
    return [comparison_factory(a, b) for a, b in combinations(proposals, 2)]
