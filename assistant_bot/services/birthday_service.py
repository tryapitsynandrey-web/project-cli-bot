"""Birthday-related service utilities."""

from __future__ import annotations

from typing import TypedDict

from assistant_bot.services.contact_service import ContactService
from assistant_bot.utils.datetime_utils import format_birthday_with_days


DEFAULT_BIRTHDAY_LOOKAHEAD_DAYS = 7


class BirthdayInfo(TypedDict):
    """Structured birthday output item."""

    contact_id: str
    name: str
    birthday: str | None
    days_left: int
    formatted: str


class BirthdayService:
    """Service for birthday-related operations."""

    def __init__(self, contact_service: ContactService) -> None:
        """Initialize the birthday service."""
        self.contact_service = contact_service

    @staticmethod
    def _normalize_days(days: int) -> int:
        """Normalize the requested birthday lookahead window."""
        return days if days > 0 else DEFAULT_BIRTHDAY_LOOKAHEAD_DAYS

    def get_upcoming_birthdays(self, days: int = DEFAULT_BIRTHDAY_LOOKAHEAD_DAYS) -> list[BirthdayInfo]:
        """Return contacts with birthdays in the next given number of days."""
        normalized_days = self._normalize_days(days)
        upcoming = self.contact_service.get_contacts_with_birthday_in_days(normalized_days)

        return [
            BirthdayInfo(
                contact_id=contact.contact_id,
                name=contact.name,
                birthday=contact.birthday,
                days_left=days_left,
                formatted=format_birthday_with_days(contact.birthday, days_left),
            )
            for contact, days_left in upcoming
        ]