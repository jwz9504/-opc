from __future__ import annotations

from dataclasses import dataclass

from .services.checkpoint import InMemoryCheckpointer
from .state import MeetingState


class HumanInterrupt(Exception):
    def __init__(self, payload: dict[str, object]) -> None:
        super().__init__(payload.get("reason", "human input required"))
        self.payload = payload


@dataclass
class StubWorkflow:
    checkpointer: InMemoryCheckpointer
    max_rounds: int = 3
    require_governance_confirmation: bool = True

    def run(self, thread_id: str, *, confirmed: bool = False, resume: bool = False) -> MeetingState:
        state = self.checkpointer.get(thread_id) if resume else None
        state = state or MeetingState(thread_id=thread_id)
        if state.cancelled:
            return state
        if self.require_governance_confirmation and not confirmed and not state.summaries.get("governance_confirmed"):
            state = state.model_copy(update={"phase": "human_confirm_governance", "human_pending": True})
            self.checkpointer.put(state)
            raise HumanInterrupt({"reason": "governance_confirmation_required", "allowed_operations": ["confirm", "modify", "cancel"]})
        state = state.model_copy(update={"summaries": {**state.summaries, "governance_confirmed": True}, "human_pending": False})
        for phase in ("research", "ideation", "selection", "revision", "quality_gates"):
            state = state.model_copy(update={"phase": phase})
            self.checkpointer.put(state)
        state = state.model_copy(update={"phase": "human_final_approval", "human_pending": True})
        self.checkpointer.put(state)
        raise HumanInterrupt({"reason": "final_approval_required", "allowed_operations": ["approve", "reject", "revise"]})

    def resume_governance(self, thread_id: str, decision: str) -> MeetingState:
        state = self.checkpointer.get(thread_id)
        if state is None:
            raise KeyError(thread_id)
        if state.phase != "human_confirm_governance":
            return state
        if decision == "cancel":
            state = state.model_copy(update={"phase": "cancelled", "cancelled": True, "human_pending": False})
        elif decision == "confirm":
            state = state.model_copy(update={"summaries": {**state.summaries, "governance_confirmed": True}, "human_pending": False})
            for phase in ("research", "ideation", "selection", "revision", "quality_gates"):
                state = state.model_copy(update={"phase": phase})
                self.checkpointer.put(state)
            state = state.model_copy(update={"phase": "human_final_approval", "human_pending": True})
        else:
            state = state.model_copy(update={"phase": "human_confirm_governance", "human_pending": True})
        self.checkpointer.put(state)
        return state

    def resume_final(self, thread_id: str, decision: str) -> MeetingState:
        state = self.checkpointer.get(thread_id)
        if state is None:
            raise KeyError(thread_id)
        if decision == "approve":
            state = state.model_copy(update={"phase": "frozen_final", "human_pending": False, "active_ids": {**state.active_ids, "final": "approved"}})
        elif decision == "reject":
            state = state.model_copy(update={"phase": "cancelled", "human_pending": False, "cancelled": True})
        else:
            state = state.model_copy(update={"phase": "revision", "human_pending": False, "round": state.round + 1})
            if state.round > self.max_rounds:
                state = state.model_copy(update={"phase": "human_escalation", "human_pending": True})
        self.checkpointer.put(state)
        return state
