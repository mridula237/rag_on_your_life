from __future__ import annotations
from dataclasses import dataclass, field
from typing import Dict, List

@dataclass
class ChatTurn:
    role: str  # "user" | "assistant"
    content: str

@dataclass
class ChatMemory:
    summary: str = ""
    turns: List[ChatTurn] = field(default_factory=list)

_MEMORY: Dict[str, ChatMemory] = {}

def get_memory(session_id: str) -> ChatMemory:
    if session_id not in _MEMORY:
        _MEMORY[session_id] = ChatMemory()
    return _MEMORY[session_id]

def append_turn(session_id: str, role: str, content: str) -> None:
    mem = get_memory(session_id)
    mem.turns.append(ChatTurn(role=role, content=content))

def set_summary(session_id: str, summary: str) -> None:
    mem = get_memory(session_id)
    mem.summary = summary
