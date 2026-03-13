"""Domain package exports."""

from __future__ import annotations

from assistant_bot.domain.contacts import Contact
from assistant_bot.domain.exceptions import (
    ContactNotFoundError,
    NoteNotFoundError,
    NotFoundError,
    PersonalAssistantError,
    StorageError,
    ValidationError,
)
from assistant_bot.domain.notes import Note

__all__ = [
    "Contact",
    "ContactNotFoundError",
    "Note",
    "NoteNotFoundError",
    "NotFoundError",
    "PersonalAssistantError",
    "StorageError",
    "ValidationError",
]