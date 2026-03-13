from __future__ import annotations

from copy import deepcopy
from typing import Any

from assistant_bot.domain.contacts import Contact
from assistant_bot.domain.notes import Note


class FakeContactRepository:
    """In-memory fake repository for contacts."""

    def __init__(self, contacts: list[Contact] | None = None) -> None:
        self._contacts: list[Contact] = list(contacts or [])
        self.save_calls = 0
        self.saved_snapshots: list[list[dict[str, Any]]] = []

    def load_all(self) -> list[Contact]:
        """Return all stored contacts."""
        return list(self._contacts)

    def save_all(self, contacts: list[Contact]) -> None:
        """Persist all contacts in memory."""
        self.save_calls += 1
        self._contacts = list(contacts)
        self.saved_snapshots.append(
            deepcopy([contact.to_dict() for contact in contacts])
        )

    def seed_contacts(self, payloads: list[dict[str, Any]]) -> None:
        """Seed repository from serialized contact payloads."""
        self._contacts = [Contact.from_dict(payload) for payload in payloads]


class FakeNoteRepository:
    """In-memory fake repository for notes."""

    def __init__(self, notes: list[Note] | None = None) -> None:
        self._notes: list[Note] = list(notes or [])
        self.save_calls = 0
        self.saved_snapshots: list[list[dict[str, Any]]] = []

    def load_all(self) -> list[Note]:
        """Return all stored notes."""
        return list(self._notes)

    def save_all(self, notes: list[Note]) -> None:
        """Persist all notes in memory."""
        self.save_calls += 1
        self._notes = list(notes)
        self.saved_snapshots.append(
            deepcopy([note.to_dict() for note in notes])
        )

    def seed_notes(self, payloads: list[dict[str, Any]]) -> None:
        """Seed repository from serialized note payloads."""
        self._notes = [Note.from_dict(payload) for payload in payloads]