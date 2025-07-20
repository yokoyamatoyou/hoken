from dataclasses import dataclass, field
from typing import List, Dict, Protocol
import json
import os


class BaseMemory(Protocol):
    """Protocol for memory implementations."""

    messages: List[Dict[str, str]]

    def add(self, role: str, content: str) -> None:
        ...

    def save(self, path: str) -> None:
        ...

    def load(self, path: str) -> None:
        ...

    def search(self, query: str, top_k: int = 3) -> List[str]:
        ...

    def clear(self) -> None:
        ...


@dataclass
class MessageMemory:
    """Common message storage with persistence helpers."""

    messages: List[Dict[str, str]] = field(default_factory=list)

    def add(self, role: str, content: str) -> None:
        """Add a message to memory."""
        self.messages.append({"role": role, "content": content})

    def save(self, path: str) -> None:
        """Persist messages to a JSON file."""
        directory = os.path.dirname(path)
        if directory:
            os.makedirs(directory, exist_ok=True)
        with open(path, "w", encoding="utf-8") as f:
            json.dump({"messages": self.messages}, f, ensure_ascii=False, indent=2)

    def load(self, path: str) -> None:
        """Load messages from a JSON file."""
        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)
        self.messages = data.get("messages", [])

    def clear(self) -> None:
        """Remove all stored messages."""
        self.messages.clear()


@dataclass
class ConversationMemory(MessageMemory):
    """Simple in-memory store for conversation messages."""

    def search(self, query: str, top_k: int = 3) -> List[str]:
        """Return messages containing the query text."""
        query_lower = query.lower()
        results = [
            m["content"]
            for m in self.messages
            if query_lower in m["content"].lower()
        ]
        return results[:top_k]
