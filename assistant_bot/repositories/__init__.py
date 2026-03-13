"""Repository layer exports."""

from __future__ import annotations

from assistant_bot.repositories.contact_repository import ContactRepository
from assistant_bot.repositories.json_contact_repository import JSONContactRepository
from assistant_bot.repositories.json_note_repository import JSONNoteRepository
from assistant_bot.repositories.note_repository import NoteRepository

__all__ = [
    "ContactRepository",
    "NoteRepository",
    "JSONContactRepository",
    "JSONNoteRepository",
]