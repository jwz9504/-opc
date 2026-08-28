from __future__ import annotations

import re

ROLE_TOOLS: dict[str, frozenset[str]] = {
    "researcher": frozenset({"search", "fetch"}),
    "ideator": frozenset(),
    "red_team": frozenset({"fetch"}),
    "executor": frozenset({"sandbox_execute"}),
    "editor": frozenset(),
}


def redact_sensitive(text: str) -> str:
    text = re.sub(r"(?i)(api[_-]?key|authorization|token|password)\s*[:=]\s*[^\s,;]+", r"\1=[REDACTED]", text)
    return re.sub(r"\b(?:sk|ak)-[A-Za-z0-9_-]{12,}\b", "[REDACTED]", text)


def can_use_tool(role: str, tool: str) -> bool:
    return tool in ROLE_TOOLS.get(role, frozenset())


def treat_as_untrusted_content(content: str) -> str:
    return f"<untrusted-data>\n{content}\n</untrusted-data>"
