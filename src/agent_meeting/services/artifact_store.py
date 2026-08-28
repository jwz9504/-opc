from __future__ import annotations

from dataclasses import dataclass
from datetime import UTC, datetime
from hashlib import sha256

from ..schemas.artifacts import ArtifactEnvelope, SourceSnapshot


@dataclass
class StoredArtifact:
    artifact_id: str
    payload: str
    content_hash: str
    created_at: datetime


class ArtifactStore:
    def __init__(self) -> None:
        self._items: dict[str, StoredArtifact] ={}

    def put(self, artifact_id: str, payload: str) -> StoredArtifact:
        item = StoredArtifact(artifact_id, payload, sha256(payload.encode()).hexdigest(), datetime.now(UTC))
        self._items.setdefault(artifact_id, item)
        return self._items[artifact_id]

    def get(self, artifact_id: str) -> StoredArtifact | None:
        return self._items.get(artifact_id)


def source_snapshot(uri: str, content: str, envelope: ArtifactEnvelope) -> SourceSnapshot:
    return SourceSnapshot(envelope=envelope, uri=uri, content_hash=sha256(content.encode()).hexdigest(), retrieved_at=datetime.now(UTC))
