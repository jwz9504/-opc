from __future__ import annotations

from dataclasses import dataclass
from datetime import UTC, datetime
from hashlib import sha256
from typing import Protocol

from ..security.boundary import treat_as_untrusted_content


@dataclass(frozen=True)
class RetrievalResult:
    uri: str
    title: str
    content: str
    content_hash: str
    retrieved_at: datetime


class RetrievalProvider(Protocol):
    def search(self, query: str) -> list[RetrievalResult]:
        ...


class StubRetrievalProvider:
    def search(self, query: str) -> list[RetrievalResult]:
        content = treat_as_untrusted_content(f"Stub evidence for: {query}")
        return [RetrievalResult("stub://source/1", "Stub Source", content, sha256(content.encode()).hexdigest(), datetime.now(UTC))]
