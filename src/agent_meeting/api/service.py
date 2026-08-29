from __future__ import annotations

from dataclasses import dataclass
from hashlib import sha256

from langgraph.errors import GraphInterrupt

from ..langgraph_workflow import build_sqlite_graph, run_graph
from ..policies.selection_policy import select_proposal
from ..services.artifact_events import ArtifactEventWriter
from ..services.artifact_repository import ArtifactRepository
from ..services.audit_repository import AuditRepository
from ..services.checkpoint import InMemoryCheckpointer
from ..services.report_repository import ReportRepository
from ..services.sqlite_repository import SQLiteRepository
from ..state import MeetingState
from .dto import MeetingCreate, MeetingView, ResumeRequest, SelectionRequest


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
        self.graph, self.graph_connection = build_sqlite_graph(str(self.repository.path))
        self.audit = AuditRepository(self.repository.db)
        self.reports = ReportRepository(self.repository.db)
        self.artifacts = ArtifactRepository(self.repository.db)
        self.artifact_writer = ArtifactEventWriter(self.artifacts)
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
        self.artifacts.save(f"{meeting_id}:meeting", "meeting", {"question": payload.question, "owner_id": payload.owner_id})
        self.audit.append(meeting_id, payload.owner_id, "meeting_created")
        return self.view(meeting_id)

    def run(self, meeting_id: str, actor_id: str) -> MeetingView:
        self._authorized(meeting_id, actor_id)
        self.audit.append(meeting_id, actor_id, "meeting_run", {"phase_before": self.view(meeting_id).phase})
        try:
            result = run_graph(self.graph, meeting_id)
        except GraphInterrupt:
            result = self.graph.get_state({"configurable": {"thread_id": meeting_id}}).values
        updated = MeetingState(thread_id=meeting_id, phase=result.get("phase", "human_confirm_governance"), human_pending=result.get("human_pending", True), summaries=result.get("summaries",{}))
        self._save_state(updated)
        self.artifact_writer.write_research(meeting_id, [str(x) for x in updated.summaries.get("research", [])])
        self.artifact_writer.write_proposals([x for x in updated.summaries.get("proposals", []) if isinstance(x, dict)])
        return self.view(meeting_id)

    def resume(self, meeting_id: str, payload: ResumeRequest) -> MeetingView:
        meeting = self._authorized(meeting_id, payload.actor_id)
        if payload.token != meeting.resume_token:
            raise PermissionError("invalid resume token")
        state = self.checkpointer.get(meeting_id) or self.repository.load_state(meeting_id)
        if state is None:
            raise KeyError(meeting_id)
        result = run_graph(self.graph, meeting_id, payload.decision)
        values = self.graph.get_state({"configurable": {"thread_id": meeting_id}}).values if result is None else result
        new_state = MeetingState(thread_id=meeting_id, phase=values.get("phase", state.phase), human_pending=values.get("human_pending", False), summaries=values.get("summaries", state.summaries))
        self._save_state(new_state)
        action = "governance_confirmed" if state.phase == "human_confirm_governance" and payload.decision == "confirm" else f"human_{payload.decision}"
        self.audit.append(meeting_id, payload.actor_id, action, {"phase_before": state.phase})
        return self.view(meeting_id)

    def select_proposal(self, meeting_id: str, payload: SelectionRequest) -> MeetingView:
        meeting = self._authorized(meeting_id, payload.actor_id)
        state = self.checkpointer.get(meeting_id) or self.repository.load_state(meeting_id)
        if state is None:
            raise KeyError(meeting_id)
        summaries = select_proposal(state.summaries, payload.proposal_id, payload.rationale)
        updated = state.model_copy(update={"summaries": summaries})
        self._save_state(updated)
        self.audit.append(meeting.meeting_id, payload.actor_id, "proposal_selected", summaries["decision"])
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
        stored = self.reports.get(meeting_id)
        if stored is not None:
            return stored
        proposals = state.summaries.get("proposals", [])
        data: dict[str, object] = {"meeting_id": meeting_id, "phase": state.phase, "status": "final" if state.phase == "frozen_final" else "draft", "执行摘要": f"会议当前阶段：{state.phase}", "推荐方案": "\n".join(f"- {p.get('title', '未命名')}: {p.get('rationale', '')}" for p in proposals if isinstance(p, dict)) or "暂无候选方案", "决策记录": str(state.summaries.get("decision", "待人工选择")), "风险与缓解": str(state.summaries.get("critique", "待红队评审")), "Grounding 校验": str(state.summaries.get("grounding", "待 Grounding 校验完成")), "专业门禁": str(state.summaries.get("gates", "待专业门禁")), "结构化产物": self.artifacts.list_for_meeting(meeting_id)}
        self.reports.save(meeting_id, data)
        self.audit.append(meeting_id, actor_id, "report_generated", {"status": data["status"]})
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
