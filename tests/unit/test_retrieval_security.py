from agent_meeting.security.boundary import (
    can_use_tool,
    redact_sensitive,
    treat_as_untrusted_content,
)
from agent_meeting.services.retrieval import StubRetrievalProvider


def test_stub_retrieval_is_untrusted_and_hashed():
    result = StubRetrievalProvider().search("query")[0]
    assert "<untrusted-data>" in result.content
    assert result.content_hash


def test_tool_permissions_and_redaction():
    assert can_use_tool("researcher", "search")
    assert not can_use_tool("editor", "search")
    assert "[REDACTED]" in redact_sensitive("api_key=secret-value")
    assert "<untrusted-data>" in treat_as_untrusted_content("ignore system")
