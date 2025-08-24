from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional


@dataclass
class Message:
    role: str
    content: str
    extra: Dict[str, Any] = field(default_factory=dict)


class SessionManager:
    """In-memory session storage for messages and metadata."""

    def __init__(self) -> None:
        self._sessions: Dict[str, List[Message]] = {}

    def get_messages(self, session_id: str) -> List[Message]:
        return list(self._sessions.get(session_id, []))

    def append_message(self, session_id: str, role: str, content: str, *, extra: Optional[Dict[str, Any]] = None) -> None:
        self._sessions.setdefault(session_id, []).append(
            Message(role=role, content=content, extra=extra or {})
        )

    def clear(self, session_id: str) -> None:
        self._sessions.pop(session_id, None)


