"""JSON-backed note repository."""

from __future__ import annotations

from collections.abc import Iterable

from assistant_bot.domain.notes import Note
from assistant_bot.repositories.note_repository import NoteRepository
from assistant_bot.storage.base import BaseStorage


class JSONNoteRepository(NoteRepository):
    """JSON-backed repository for notes."""

    def __init__(self, storage: BaseStorage) -> None:
        """Initialize repository with a storage backend."""
        self.storage = storage

    def load_all(self) -> list[Note]:
        """Load all notes from storage."""
        return self.storage.load_notes()

    def save_all(self, notes: Iterable[Note]) -> None:
        """Persist all notes to storage."""
        self.storage.save_notes(list(notes))