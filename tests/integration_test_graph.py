import pytest

from agent_meeting.graph import HumanInterrupt, StubWorkflow
from agent_meeting.services.checkpoint import InMemoryCheckpointer


def test_governance_interrupt_and_resume():
    cp = InMemoryCheckpointer()
    flow = StubWorkflow(cp)
    with pytest.raises(HumanInterrupt) as exc:
        flow.run("t1")
    assert exc.value.payload["reason"] == "governance_confirmation_required"
    state = flow.run("t1", confirmed=True, resume=True)
    assert state.phase == "human_final_approval"
    assert state.human_pending
    restored = InMemoryCheckpointer()
    restored.put(state)
    assert restored.get("t1").phase == "human_final_approval"


def test_final_approval_paths():
    cp = InMemoryCheckpointer()
    flow = StubWorkflow(cp)
    with pytest.raises(HumanInterrupt):
        flow.run("t2", confirmed=True)
    assert flow.resume_final("t2", "approve").phase == "frozen_final"
    with pytest.raises(HumanInterrupt):
        flow.run("t3", confirmed=True)
    assert flow.resume_final("t3", "reject").cancelled
