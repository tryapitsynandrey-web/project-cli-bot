"""JSON-backed contact repository."""

from __future__ import annotations

from collections.abc import Iterable

from assistant_bot.domain.contacts import Contact
from assistant_bot.repositories.contact_repository import ContactRepository
from assistant_bot.storage.base import BaseStorage


class JSONContactRepository(ContactRepository):
    """JSON-backed repository for contacts."""

    def __init__(self, storage: BaseStorage) -> None:
        """Initialize repository with a storage backend."""
        self.storage = storage

    def load_all(self) -> list[Contact]:
        """Load all contacts from storage."""
        return self.storage.load_contacts()

    def save_all(self, contacts: Iterable[Contact]) -> None:
        """Persist all contacts to storage."""
        self.storage.save_contacts(list(contacts))