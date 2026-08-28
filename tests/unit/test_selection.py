from agent_meeting.nodes.research import stub_ideation
from agent_meeting.policies.proposal import normalize_proposal, shortlist
from agent_meeting.policies.selection import build_decision_record, disposition_from_comparisons
from agent_meeting.schemas.artifacts import ProposalComparison


def test_tie_becomes_pareto_candidate():
    proposals = shortlist([normalize_proposal(p) for p in stub_ideation("m4")])
    a, b = proposals[:2]
    comparison = ProposalComparison(envelope=a.envelope, proposal_a_id=a.envelope.artifact_id, proposal_b_id=b.envelope.artifact_id, outcome="tie", confidence=0.8)
    dispositions = disposition_from_comparisons(proposals[:2], [comparison])
    assert all(d.disposition == "pareto_candidate" for d in dispositions)


def test_decision_keeps_rejected_ids():
    proposals = shortlist([normalize_proposal(p) for p in stub_ideation("m5")])
    dispositions = [
        *[__import__('agent_meeting.schemas.artifacts', fromlist=['ProposalDisposition']).ProposalDisposition(envelope=p.envelope, proposal_id=p.envelope.artifact_id, disposition="rejected", reasons=["test"]) for p in proposals[1:]],
    ]
    record = build_decision_record(proposals[0].envelope, dispositions, "人工选择首选方向", proposals[0].envelope.artifact_id)
    assert len(record.rejected_proposal_ids) == 2
