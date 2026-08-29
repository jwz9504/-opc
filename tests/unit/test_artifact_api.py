from agent_meeting.api.app import app


def test_artifact_route_exists():
    routes = {route.path for route in app.routes}
    assert "/meetings/{meeting_id}/artifacts" in routes
