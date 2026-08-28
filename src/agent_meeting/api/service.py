from __future__ import annotations

from dataclasses import dataclass
from hashlib import sha256

from ..graph import HumanInterrupt, StubWorkflow
from ..services.checkpoint import InMemoryCheckpointer
from ..state import MeetingState
from .dto import MeetingCreate, MeetingView, ResumeRequest


@dataclass
class Meeting:
    meeting_id: str
    owner_id: str
    question: str
    resume_token: str


class MeetingService:
    def __init__(self) -> None:
        self.checkpointer = InMemoryCheckpointer()
        self.workflow = StubWorkflow(self.checkpointer)
        self.meetings: dict[str, Meeting] ={}
        self.requests: dict[str, str] ={}

    def create(self, payload: MeetingCreate, request_key: str) -> MeetingView:
        if request_key in self.requests:
            return self.view(self.requests[request_key])
        meeting_id = sha256(f"{payload.owner_id + payload.question}".encode()).hexdigest()[:16]
        token = sha256(f"{meeting_id}:resume".encode()).hexdigest()
        self.meetings[meeting_id] = Meeting(meeting_id, payload.owner_id, payload.question, token)
        self.requests[request_key] = meeting_id
        self.checkpointer.put(MeetingState(thread_id=meeting_id))
        return self.view(meeting_id)

    def run(self, meeting_id: str, actor_id: str) -> MeetingView:
        meeting = self._authorized(meeting_id, actor_id)
        try:
            self.workflow.run(meeting.meeting_id)
        except HumanInterrupt:
            pass
        return self.view(meeting_id)

    def resume(self, meeting_id: str, payload: ResumeRequest) -> MeetingView:
        meeting = self._authorized(meeting_id, payload.actor_id)
        if payload.token != meeting.resume_token:
            raise PermissionError("invalid resume token")
        state = self.checkpointer.get(meeting_id)
        if state is None:
            raise KeyError(meeting_id)
        if state.phase == "human_confirm_governance":
            self.workflow.resume_governance(meeting_id, payload.decision)
        else:
            decision = "approve" if payload.decision == "confirm" else payload.decision
            self.workflow.resume_final(meeting_id, decision)
        return self.view(meeting_id)

    def view(self, meeting_id: str) -> MeetingView:
        meeting = self.meetings[meeting_id]
        state = self.checkpointer.get(meeting_id)
        if state is None:
            raise KeyError(meeting_id)
        return MeetingView(meeting_id=meeting_id, owner_id=meeting.owner_id, phase=state.phase, human_pending=state.human_pending)

    def _authorized(self, meeting_id: str, actor_id: str) -> Meeting:
        meeting = self.meetings[meeting_id]
        if meeting.owner_id != actor_id:
            raise PermissionError("meeting access denied")
        return meeting
