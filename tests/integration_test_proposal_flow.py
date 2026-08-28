from agent_meeting.nodes.research import stub_ideation
from agent_meeting.policies.proposal import (
    deduplicate_proposals,
    filter_proposals,
    normalize_proposal,
    shortlist,
)


def test_stub_generates_three_distinct_proposals():
    proposals = stub_ideation("m1")
    assert len(proposals) == 3
    assert len({p.title for p in proposals}) == 3


def test_normalize_dedupe_and_filter():
    proposals = [normalize_proposal(p) for p in stub_ideation("m2")]
    assert len(deduplicate_proposals(proposals)) == 3
    dispositions = filter_proposals(proposals, {"budget"})
    assert all(d.disposition == "eligible" for d in dispositions)


def test_shortlist_limit():
    proposals = [normalize_proposal(p) for p in stub_ideation("m3")]
    assert len(shortlist(proposals, limit=2)) == 2
