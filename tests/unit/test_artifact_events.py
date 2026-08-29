import sqlite3

from agent_meeting.nodes.research import stub_ideation, stub_research
from agent_meeting.services.artifact_events import ArtifactEventWriter
from agent_meeting.services.artifact_repository import ArtifactRepository


def test_writer_persists_research_and_proposals():
    db = sqlite3.connect(":memory:")
    repo = ArtifactRepository(db)
    writer = ArtifactEventWriter(repo)
    writer.write_research("m1", stub_research("m1"))
    count = writer.write_proposals([p.model_dump(mode="json") for p in stub_ideation("m1")])
    items = repo.list_for_meeting("m1")
    assert count == 3
    assert len(items) == 4
