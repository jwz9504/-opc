from __future__ import annotations

from typing import Any, TypedDict

from langgraph.checkpoint.memory import InMemorySaver
from langgraph.graph import END, START, StateGraph
from langgraph.types import Command, interrupt


class GraphState(TypedDict, total=False):
    thread_id: str
    phase: str
    human_pending: bool
    governance_confirmed: bool
    final_approved: bool
    summaries: dict[str, Any]


def _governance(state: GraphState) -> dict[str, Any]:
    if not state.get("governance_confirmed"):
        answer = interrupt({"reason": "governance_confirmation_required", "allowed_operations": ["confirm", "cancel"]})
        if answer == "cancel":
            return {"phase": "cancelled", "human_pending": False}
        return {"governance_confirmed": True, "human_pending": False, "phase": "research"}
    return {"phase": "research"}


def _work(state: GraphState) -> dict[str, Any]:
    return {"phase": "human_final_approval", "human_pending": True, "summaries": {"stub": "research_and_ideation_complete"}}


def _final(state: GraphState) -> dict[str, Any]:
    answer = interrupt({"reason": "final_approval_required", "allowed_operations": ["approve", "reject"]})
    if answer == "approve":
        return {"phase": "frozen_final", "human_pending": False, "final_approved": True}
    return {"phase": "cancelled", "human_pending": False}


def build_graph(checkpointer: InMemorySaver | None = None) -> Any:
    builder = StateGraph(GraphState)
    builder.add_node("governance", _governance)
    builder.add_node("work", _work)
    builder.add_node("final", _final)
    builder.add_edge(START, "governance")
    builder.add_edge("governance", "work")
    builder.add_edge("work", "final")
    builder.add_edge("final", END)
    return builder.compile(checkpointer=checkpointer or InMemorySaver())


def run_graph(graph: Any, thread_id: str, resume_value: Any | None = None) -> Any:
    config = {"configurable": {"thread_id": thread_id}}
    if resume_value is None:
        return graph.invoke({"thread_id": thread_id, "phase": "intake"}, config)
    return graph.invoke(Command(resume=resume_value), config)
