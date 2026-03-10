"""Birthday-related service utilities."""

from typing import TypedDict

from assistant_bot.services.contact_service import ContactService
from assistant_bot.utils.datetime_utils import format_birthday_with_days


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

    def get_upcoming_birthdays(self, days: int = 7) -> list[BirthdayInfo]:
        """Return contacts with birthdays in the next given number of days."""
        if days < 1:
            days = 7

        upcoming = self.contact_service.get_contacts_with_birthday_in_days(days)

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