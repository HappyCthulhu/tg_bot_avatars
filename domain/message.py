from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from typing import Literal


@dataclass(slots=True)
class Message:
    sender: Literal["user", "assistant"]
    text: str
    timestamp: datetime

    def to_redis_dict(self) -> dict[str, str]:
        return {
            "sender": self.sender,
            "text": self.text,
            "timestamp": self.timestamp.isoformat(),
        }

    @classmethod
    def from_redis_dict(cls, payload: dict[str, str]) -> Message:
        return cls(
            sender=payload["sender"],  # type: ignore[arg-type]
            text=payload["text"],
            timestamp=datetime.fromisoformat(payload["timestamp"]),
        )
