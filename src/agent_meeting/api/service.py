from __future__ import annotations

from dataclasses import dataclass
from hashlib import sha256

from ..graph import HumanInterrupt, StubWorkflow
from ..services.audit_repository import AuditRepository
from ..services.checkpoint import InMemoryCheckpointer
from ..services.report_repository import ReportRepository
from ..services.sqlite_repository import SQLiteRepository
from ..state import MeetingState
from .dto import MeetingCreate, MeetingView, ResumeRequest


@dataclass
class Meeting:
    meeting_id: str
    owner_id: str
    question: str
    resume_token: str

class MeetingService:
    def __init__(self, repository: SQLiteRepository | None = None) -> None:
        self.repository = repository or SQLiteRepository()
        self.checkpointer = InMemoryCheckpointer()
        self.workflow = StubWorkflow(self.checkpointer)
        self.audit = AuditRepository(self.repository.db)
        self.reports = ReportRepository(self.repository.db)
        self.meetings: dict[str, Meeting] ={}
        self.requests: dict[str, str] ={}

    def create(self, payload: MeetingCreate, request_key: str) -> MeetingView:
        existing = self.repository.get_by_request(request_key)
        if existing:
            return self.view(existing)
        meeting_id = sha256(f"{payload.owner_id + payload.question}".encode()).hexdigest()[:16]
        token = sha256(f"{meeting_id}:resume".encode()).hexdigest()
        meeting = Meeting(meeting_id, payload.owner_id, payload.question, token)
        self.meetings[meeting_id] = meeting
        self.requests[request_key] = meeting_id
        self.repository.save_meeting(meeting_id, meeting.owner_id, meeting.question, meeting.resume_token, request_key)
        self._save_state(MeetingState(thread_id=meeting_id))
        self.audit.append(meeting_id, payload.owner_id, "meeting_created")
        return self.view(meeting_id)

    def run(self, meeting_id: str, actor_id: str) -> MeetingView:
        self._authorized(meeting_id, actor_id)
        try:
            self.workflow.run(meeting_id, resume=True)
        except HumanInterrupt:
            pass
        return self.view(meeting_id)

    def resume(self, meeting_id: str, payload: ResumeRequest) -> MeetingView:
        meeting = self._authorized(meeting_id, payload.actor_id)
        if payload.token != meeting.resume_token:
            raise PermissionError("invalid resume token")
        state = self.checkpointer.get(meeting_id) or self.repository.load_state(meeting_id)
        if state is None:
            raise KeyError(meeting_id)
        if state.phase == "human_confirm_governance":
            new_state = self.workflow.resume_governance(meeting_id, payload.decision)
        else:
            decision = "approve" if payload.decision == "confirm" else payload.decision
            new_state = self.workflow.resume_final(meeting_id, decision)
        self._save_state(new_state)
        return self.view(meeting_id)

    def cancel(self, meeting_id: str, actor_id: str) -> MeetingView:
        self._authorized(meeting_id, actor_id)
        state = self.checkpointer.get(meeting_id) or self.repository.load_state(meeting_id)
        if state is None:
            raise KeyError(meeting_id)
        cancelled = state.model_copy(update={"phase": "cancelled", "cancelled": True, "human_pending": False})
        self._save_state(cancelled)
        self.audit.append(meeting_id, actor_id, "meeting_cancelled")
        return self.view(meeting_id)

    def report(self, meeting_id: str, actor_id: str) -> dict[str, object]:
        self._authorized(meeting_id, actor_id)
        state = self.checkpointer.get(meeting_id) or self.repository.load_state(meeting_id)
        if state is None:
            raise KeyError(meeting_id)
        data: dict[str, object] = {"meeting_id": meeting_id, "phase": state.phase, "status": "final" if state.phase == "frozen_final" else "draft"}
        self.reports.save(meeting_id, data)
        return data

    def audit_events(self, meeting_id: str, actor_id: str) -> list[dict[str, object]]:
        self._authorized(meeting_id, actor_id)
        return self.audit.for_meeting(meeting_id)

    def _authorized(self, meeting_id: str, actor_id: str) -> Meeting:
        meeting = self._load_meeting(meeting_id)
        if meeting.owner_id != actor_id:
            raise PermissionError("meeting access denied")
        return meeting

    def view(self, meeting_id: str) -> MeetingView:
        meeting = self._load_meeting(meeting_id)
        state = self.checkpointer.get(meeting_id) or self.repository.load_state(meeting_id)
        if state is None:
            raise KeyError(meeting_id)
        self.checkpointer.put(state)
        return MeetingView(meeting_id=meeting_id, owner_id=meeting.owner_id, phase=state.phase, human_pending=state.human_pending)

    def _load_meeting(self, meeting_id: str) -> Meeting:
        if meeting_id in self.meetings:
            return self.meetings[meeting_id]
        row = self.repository.get_meeting(meeting_id)
        if row is None:
            raise KeyError(meeting_id)
        meeting = Meeting(*row)
        self.meetings[meeting_id] = meeting
        return meeting

    def _save_state(self, state: MeetingState) -> None:
        self.checkpointer.put(state)
        self.repository.save_state(state)
