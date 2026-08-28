from agent_meeting.langgraph_workflow import build_graph, run_graph


def test_langgraph_interrupt_resume():
    graph = build_graph()
    run_graph(graph, "lg-1")
    assert graph.get_state({"configurable": {"thread_id": "lg-1"}}).next == ("governance",)
    second = run_graph(graph, "lg-1", "confirm")
    assert second["phase"] == "human_final_approval"
    third = run_graph(graph, "lg-1", "approve")
    assert third["phase"] == "frozen_final"
