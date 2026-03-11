"""Unified schema for all conversation sources."""

from dataclasses import dataclass, field
from datetime import datetime


@dataclass
class Turn:
    role: str           # "user" | "assistant"
    text: str           # text content only — tool blocks stripped
    timestamp: datetime


@dataclass
class Session:
    session_id: str
    source: str         # "claude-code" | "claude-ai" | "claude-desktop"
    project: str        # slug derived from cwd path, or conversation title
    ts_start: datetime
    ts_end: datetime
    turns: list[Turn] = field(default_factory=list)

    @property
    def duration_minutes(self) -> float:
        return (self.ts_end - self.ts_start).total_seconds() / 60

    @property
    def word_count(self) -> int:
        return sum(len(t.text.split()) for t in self.turns)
