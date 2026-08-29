from agent_meeting.services.model_registry import ModelConfig, ModelRegistry


def test_registry_from_environment(monkeypatch):
    monkeypatch.setenv("AGENT_MEETING_MODEL_PROVIDER", "stub")
    monkeypatch.setenv("AGENT_MEETING_MODEL_ID", "test-stub")
    config = ModelRegistry.from_environment().for_role("default")
    assert config.model_id == "test-stub"
    assert config.provider == "stub"


def test_structured_output_retries():
    registry = ModelRegistry([ModelConfig("stub", "default", max_retries=1)])
    calls = {"count": 0}

    def call():
        calls["count"] += 1
        return calls["count"]

    def validator(value):
        if value == 1:
            raise ValueError("invalid")
        return value

    assert registry.invoke_structured("default", call, validator) == 2
    assert calls["count"] == 2
