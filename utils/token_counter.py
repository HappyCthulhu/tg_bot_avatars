from __future__ import annotations

from math import ceil
from typing import Any


def count_prompt_tokens(messages: list[dict[str, Any]]) -> int:
    # Lightweight approximation to protect context window without extra dependencies.
    total_chars = sum(len(str(message.get("content", ""))) for message in messages)
    return max(1, ceil(total_chars / 4))
