from __future__ import annotations

from typing import Any

from .sqlalchemy_artifact_store import SQLAlchemyArtifactStore


class ArtifactEventWriter:
    """Persists graph-produced artifacts without coupling graph nodes to SQLite."""

    def __init__(self, repository: SQLAlchemyArtifactStore) -> None:
        self.repository = repository

    def write_proposals(self, proposals: list[dict[str, Any]]) -> int:
        count = 0
        for proposal in proposals:
            envelope = proposal.get("envelope")
            if not isinstance(envelope, dict):
                continue
            artifact_id = envelope.get("artifact_id")
            if not artifact_id:
                continue
            self.repository.save(str(artifact_id), "proposal", proposal)
            count += 1
        return count

    def write_research(self, meeting_id: str, items: list[str]) -> None:
        self.repository.save(f"{meeting_id}:research", "research", {"items": items})
