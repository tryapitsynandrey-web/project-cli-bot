"""Repository protocol for note persistence."""

from __future__ import annotations

from collections.abc import Iterable
from typing import Protocol

from assistant_bot.domain.notes import Note


class NoteRepository(Protocol):
    """Repository contract for note persistence and retrieval."""

    def load_all(self) -> list[Note]:
        """Load all notes."""
        ...

    def save_all(self, notes: Iterable[Note]) -> None:
        """Persist all notes."""
        ...