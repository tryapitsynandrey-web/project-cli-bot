"""Contact management service."""

from assistant_bot.domain.contacts import Contact
from assistant_bot.domain.exceptions import ContactNotFoundError
from assistant_bot.storage.base import BaseStorage
from assistant_bot.utils.datetime_utils import days_until_birthday
from assistant_bot.utils.validators import normalize_tag


class ContactService:
    """Service for managing contacts."""

    def __init__(self, storage: BaseStorage) -> None:
        """Initialize the contact service."""
        self.storage = storage
        self.contacts: list[Contact] = []
        self._load()

    def _load(self) -> None:
        """Load contacts from storage."""
        self.contacts = self.storage.load_contacts()

    def _save(self) -> None:
        """Persist contacts to storage."""
        self.storage.save_contacts(self.contacts)

    def add_contact(
        self,
        name: str,
        phone_numbers: list[str],
        address: str | None = None,
        email: str | None = None,
        birthday: str | None = None,
        note: str | None = None,
        tags: list[str] | None = None,
    ) -> Contact:
        """Create and store a new contact."""
        contact = Contact.create(
            name=name,
            phone_numbers=phone_numbers,
            address=address,
            email=email,
            birthday=birthday,
            note=note,
            tags=tags or [],
        )
        self.contacts.append(contact)
        self._save()
        return contact

    def get_contact(self, contact_id: str) -> Contact:
        """Return a contact by ID."""
        for contact in self.contacts:
            if contact.contact_id == contact_id:
                return contact
        raise ContactNotFoundError(f"Contact {contact_id} not found")

    def get_all_contacts(self) -> list[Contact]:
        """Return all contacts sorted by name."""
        return sorted(self.contacts, key=lambda contact: contact.name.lower())

    def update_contact(
        self,
        contact_id: str,
        name: str | None = None,
        address: str | None = None,
        email: str | None = None,
        birthday: str | None = None,
        phone_numbers: list[str] | None = None,
        note: str | None = None,
        tags: list[str] | None = None,
    ) -> Contact:
        """Update an existing contact and persist the changes."""
        contact = self.get_contact(contact_id)
        contact.update(
            name=name,
            address=address,
            email=email,
            birthday=birthday,
            note=note,
            phone_numbers=phone_numbers,
            tags=tags,
        )
        self._save()
        return contact

    def delete_contact(self, contact_id: str) -> None:
        """Delete a contact by ID."""
        contact = self.get_contact(contact_id)
        self.contacts.remove(contact)
        self._save()

    def search_contacts(self, query: str) -> list[Contact]:
        """Search contacts by text query."""
        results = [contact for contact in self.contacts if contact.matches_search(query)]
        return sorted(results, key=lambda contact: contact.name.lower())

    def get_contacts_by_name(self, name: str) -> list[Contact]:
        """Return contacts matching the provided name query."""
        return self.search_contacts(name)

    def get_contacts_by_tag(self, tag: str) -> list[Contact]:
        """Return all contacts that contain the given tag."""
        normalized_tag = normalize_tag(tag)
        if not normalized_tag:
            return []

        results = [
            contact
            for contact in self.contacts
            if normalized_tag in contact.tags
        ]
        return sorted(results, key=lambda contact: contact.name.lower())

    def get_contacts_with_birthday_in_days(self, days: int) -> list[tuple[Contact, int]]:
        """Return contacts with birthdays in the next given number of days."""
        result: list[tuple[Contact, int]] = []

        for contact in self.contacts:
            days_left = days_until_birthday(contact.birthday)
            if 0 <= days_left <= days:
                result.append((contact, days_left))

        result.sort(key=lambda item: item[1])
        return result

    def add_tag_to_contact(self, contact_id: str, tag: str) -> None:
        """Add a tag to a contact."""
        contact = self.get_contact(contact_id)
        contact.add_tag(tag)
        self._save()

    def edit_contact_tag(self, contact_id: str, old_tag: str, new_tag: str) -> None:
        """Replace one contact tag with another."""
        contact = self.get_contact(contact_id)
        contact.edit_tag(old_tag, new_tag)
        self._save()

    def delete_tag_from_contact(self, contact_id: str, tag: str) -> None:
        """Remove a tag from a contact."""
        contact = self.get_contact(contact_id)
        contact.remove_tag(tag)
        self._save()

    def get_all_contact_tags(self) -> set[str]:
        """Return all unique tags used across contacts."""
        all_tags: set[str] = set()
        for contact in self.contacts:
            all_tags.update(contact.tags)
        return all_tags