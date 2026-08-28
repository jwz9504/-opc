from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass
from typing import Any


@dataclass(frozen=True)
class ModelConfig:
    model_id: str
    role: str
    timeout_seconds: float = 30
    max_retries: int = 2
    fallback_model_id: str | None = None


class ModelRegistry:
    def __init__(self, configs: list[ModelConfig] | None = None) -> None:
        self._configs = {config.role: config for config in (configs or [])}

    def register(self, config: ModelConfig) -> None:
        self._configs[config.role] = config

    def for_role(self, role: str) -> ModelConfig:
        return self._configs[role]

    def invoke_structured(self, role: str, call: Callable[[], Any], validator: Callable[[Any], Any]) -> Any:
        config = self.for_role(role)
        last_error: Exception | None = None
        for _ in range(config.max_retries + 1):
            try:
                return validator(call())
            except (ValueError, TypeError, RuntimeError) as exc:
                last_error = exc
        raise RuntimeError(f"structured model output failed for {role}") from last_error
