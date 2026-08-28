from __future__ import annotations

from collections.abc import Iterable

from ..schemas.operations import BranchTask


def fan_in_ready(tasks: Iterable[BranchTask]) -> bool:
    items = list(tasks)
    return all(task.status == "succeeded" for task in items if task.required)


def retry_failed(tasks: Iterable[BranchTask]) -> list[BranchTask]:
    return [task.model_copy(update={"status": "pending", "attempts": task.attempts + 1}) for task in tasks if task.status == "failed"]
