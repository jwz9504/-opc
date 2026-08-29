from __future__ import annotations

import os
from collections.abc import Callable
from dataclasses import dataclass
from typing import Any


@dataclass(frozen=True)
class ModelConfig:
    model_id: str
    role: str
    provider: str = "stub"
    timeout_seconds: float = 30
    max_retries: int = 2
    fallback_model_id: str | None = None


class ModelRegistry:
    def __init__(self, configs: list[ModelConfig] | None = None) -> None:
        self._configs = {config.role: config for config in (configs or [])}

    @classmethod
    def from_environment(cls) -> ModelRegistry:
        provider = os.getenv("AGENT_MEETING_MODEL_PROVIDER", "stub")
        model_id = os.getenv("AGENT_MEETING_MODEL_ID", "stub-v1")
        return cls([ModelConfig(model_id=model_id, role="default", provider=provider)])

    def register(self, config: ModelConfig) -> None:
        self._configs[config.role] = config

    def for_role(self, role: str) -> ModelConfig:
        return self._configs.get(role, self._configs["default"])

    def invoke_structured(self, role: str, call: Callable[[], Any], validator: Callable[[Any], Any]) -> Any:
        config = self.for_role(role)
        last_error: Exception | None = None
        for _ in range(config.max_retries + 1):
            try:
                return validator(call())
            except (ValueError, TypeError, RuntimeError) as exc:
                last_error = exc
        raise RuntimeError(f"structured model output failed for {role}") from last_error
