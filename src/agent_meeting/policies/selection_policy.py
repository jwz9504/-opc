from __future__ import annotations

from typing import Any


def select_proposal(
    summaries: dict[str, Any],
    proposal_id: str,
    rationale: str,
) -> dict[str, Any]:
    """Return a copied summary with a validated human selection."""
    if not rationale.strip():
        raise ValueError("selection rationale is required")

    proposals = summaries.get("proposals", [])
    candidate_ids: list[str] = []
    for proposal in proposals:
        if not isinstance(proposal, dict):
            continue
        envelope = proposal.get("envelope")
        if isinstance(envelope, dict):
            artifact_id = envelope.get("artifact_id")
            if artifact_id:
                candidate_ids.append(str(artifact_id))

    if proposal_id not in candidate_ids:
        raise ValueError("proposal not found in candidates")

    return {
        **summaries,
        "decision": {
            "status": "selected",
            "selected_proposal_id": proposal_id,
            "candidate_ids": candidate_ids,
            "rationale": rationale.strip(),
        },
    }
