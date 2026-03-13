"""Repository protocol for contact persistence."""

from __future__ import annotations

from collections.abc import Iterable
from typing import Protocol

from assistant_bot.domain.contacts import Contact


class ContactRepository(Protocol):
    """Repository contract for contact persistence and retrieval."""

    def load_all(self) -> list[Contact]:
        """Load all contacts."""
        ...

    def save_all(self, contacts: Iterable[Contact]) -> None:
        """Persist all contacts."""
        ...