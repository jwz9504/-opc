from agent_meeting.policies.selection_policy import select_proposal


def test_select_proposal_returns_decision():
    summaries = {"proposals": [{"envelope": {"artifact_id": "p1"}, "title": "A"}, {"envelope": {"artifact_id": "p2"}, "title": "B"}]}
    updated = select_proposal(summaries, "p2", "成本更低")
    assert updated["decision"]["selected_proposal_id"] == "p2"
    assert summaries.get("decision") is None


def test_select_proposal_rejects_unknown():
    import pytest
    with pytest.raises(ValueError):
        select_proposal({"proposals": []}, "missing", "理由")
