from __future__ import annotations

import json
from copy import deepcopy
from pathlib import Path

from ..state import MeetingState


class CheckpointStore:
    """Small JSON checkpoint store used by the development Stub workflow."""

    def __init__(self, root: str | Path) -> None:
        self.root = Path(root)
        self.root.mkdir(parents=True, exist_ok=True)

    def save(self, state: MeetingState) -> MeetingState:
        path = self.root / f"{state.thread_id}.json"
        path.write_text(state.model_dump_json(indent=2), encoding="utf-8")
        return state

    def load(self, thread_id: str) -> MeetingState | None:
        path = self.root / f"{thread_id}.json"
        if not path.exists():
            return None
        return MeetingState.model_validate(json.loads(path.read_text(encoding="utf-8")))


class InMemoryCheckpointer:
    def __init__(self) -> None:
        self._states: dict[str, MeetingState] ={}

    def put(self, state: MeetingState) -> MeetingState:
        self._states[state.thread_id] = deepcopy(state)
        return state

    def get(self, thread_id: str) -> MeetingState | None:
        state = self._states.get(thread_id)
        return deepcopy(state) if state else None
