"""Abstract base class for storage backends."""

from __future__ import annotations

from abc import ABC, abstractmethod

from assistant_bot.domain.contacts import Contact
from assistant_bot.domain.notes import Note


class BaseStorage(ABC):
    """Abstract base class for persistent storage backends."""

    @abstractmethod
    def load_contacts(self) -> list[Contact]:
        """Load all contacts from storage."""

    @abstractmethod
    def save_contacts(self, contacts: list[Contact]) -> None:
        """Save all contacts to storage."""

    @abstractmethod
    def load_notes(self) -> list[Note]:
        """Load all notes from storage."""

    @abstractmethod
    def save_notes(self, notes: list[Note]) -> None:
        """Save all notes to storage."""