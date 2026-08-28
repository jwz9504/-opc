from __future__ import annotations

import json
from typing import Any

FIXED_SECTIONS = ["执行摘要", "推荐方案", "实施步骤", "风险与缓解", "决策记录", "少数派意见", "行动项", "证据与引用附录", "会议审计摘要"]


def render_markdown(data: dict[str, Any]) -> str:
    lines = [f"# {data.get('title', '会议报告')}"]
    for section in FIXED_SECTIONS:
        lines.extend([f"## {section}", str(data.get(section, "待补充")), ""])
    return "\n".join(lines)


def render_json(data: dict[str, Any]) -> str:
    return json.dumps(data, ensure_ascii=False, sort_keys=True, indent=2)
