from __future__ import annotations

import json
from hashlib import sha256
from threading import Lock

from ..schemas.operations import OperationRecord, OutboxEvent


def idempotency_key(thread_id: str, checkpoint_id: str, node_name: str, logical_input: object, operation_type: str) -> str:
    raw = json.dumps([thread_id, checkpoint_id, node_name, logical_input, operation_type], sort_keys=True, default=str)
    return sha256(raw.encode()).hexdigest()


class OperationLedger:
    def __init__(self) -> None:
        self._records: dict[str, OperationRecord] ={}
        self._lock = Lock()

    def plan(self, record: OperationRecord) -> OperationRecord:
        with self._lock:
            return self._records.setdefault(record.idempotency_key, record)

    def get(self, key: str) -> OperationRecord | None:
        return self._records.get(key)


class Outbox:
    def __init__(self) -> None:
        self._events: dict[str, OutboxEvent] ={}

    def enqueue(self, event: OutboxEvent) -> OutboxEvent:
        return self._events.setdefault(event.event_id, event)

    def pending(self) -> list[OutboxEvent]:
        return [event for event in self._events.values() if event.status == "pending"]

    def confirm(self, event_id: str) -> OutboxEvent:
        event = self._events[event_id].model_copy(update={"status": "confirmed"})
        self._events[event_id] = event
        return event
