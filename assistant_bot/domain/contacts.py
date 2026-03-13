"""Contact domain model."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
import uuid

from assistant_bot.utils.validators import (
    normalize_tag,
    validate_address,
    validate_birthday,
    validate_email,
    validate_name,
    validate_phone,
    validate_tag,
)


def _generate_id() -> str:
    """Return a new unique identifier."""
    return str(uuid.uuid4())


def _timestamp_now() -> str:
    """Return the current timestamp in ISO format."""
    return datetime.now().isoformat()


@dataclass(slots=True)
class Contact:
    """Represent a contact with personal data and tags."""

    name: str
    phone_numbers: list[str]
    address: str | None = None
    email: str | None = None
    birthday: str | None = None
    note: str | None = None
    tags: list[str] = field(default_factory=list)
    contact_id: str = field(default_factory=_generate_id)
    created_at: str = field(default_factory=_timestamp_now)

    @classmethod
    def create(
        cls,
        name: str,
        phone_numbers: list[str],
        address: str | None = None,
        email: str | None = None,
        birthday: str | None = None,
        note: str | None = None,
        tags: list[str] | None = None,
    ) -> "Contact":
        """Create a validated contact instance."""
        validated_name = validate_name(name)
        validated_phones = [
            validate_phone(phone)
            for phone in phone_numbers
            if phone
        ]

        if not validated_phones:
            raise ValueError("At least one phone number is required")

        validated_address = validate_address(address) if address else None
        validated_email = validate_email(email) if email else None
        validated_birthday = validate_birthday(birthday) if birthday else None
        normalized_note = cls._normalize_note(note)
        normalized_tags = cls._normalize_tags(tags or [])

        return cls(
            name=validated_name,
            phone_numbers=validated_phones,
            address=validated_address,
            email=validated_email,
            birthday=validated_birthday,
            note=normalized_note,
            tags=normalized_tags,
        )

    def update(
        self,
        name: str | None = None,
        address: str | None = None,
        email: str | None = None,
        birthday: str | None = None,
        note: str | None = None,
        phone_numbers: list[str] | None = None,
        tags: list[str] | None = None,
    ) -> None:
        """Update contact fields with validation."""
        if name is not None:
            self.name = validate_name(name)

        if address is not None:
            self.address = validate_address(address) if address else None

        if email is not None:
            self.email = validate_email(email) if email else None

        if birthday is not None:
            self.birthday = validate_birthday(birthday) if birthday else None

        if note is not None:
            self.note = self._normalize_note(note)

        if phone_numbers is not None:
            validated_phones = [
                validate_phone(phone)
                for phone in phone_numbers
                if phone
            ]
            if not validated_phones:
                raise ValueError("At least one phone number is required")
            self.phone_numbers = validated_phones

        if tags is not None:
            self.tags = self._normalize_tags(tags)

    def add_tag(self, tag: str) -> None:
        """Add a validated tag if it is not already present."""
        validated = validate_tag(tag)
        if validated not in self.tags:
            self.tags.append(validated)

    def edit_tag(self, old_tag: str, new_tag: str) -> None:
        """Replace one tag with another validated tag."""
        old_normalized = normalize_tag(old_tag)
        validated_new_tag = validate_tag(new_tag)

        if old_normalized not in self.tags:
            return

        updated_tags = [
            validated_new_tag if tag == old_normalized else tag
            for tag in self.tags
        ]
        self.tags = self._normalize_tags(updated_tags)

    def remove_tag(self, tag: str) -> None:
        """Remove a normalized tag from the contact."""
        normalized = normalize_tag(tag)
        if normalized in self.tags:
            self.tags.remove(normalized)

    @staticmethod
    def _normalize_note(note: str | None) -> str | None:
        """Normalize note text to a clean optional value."""
        if note is None:
            return None
        cleaned = note.strip()
        return cleaned if cleaned else None

    @staticmethod
    def _normalize_tags(tags: list[str]) -> list[str]:
        """Normalize, validate, filter, and deduplicate tags while preserving order."""
        normalized_tags: list[str] = []
        seen: set[str] = set()

        for tag in tags:
            normalized = normalize_tag(tag)
            if not normalized:
                continue

            validated = validate_tag(normalized)
            if validated in seen:
                continue

            normalized_tags.append(validated)
            seen.add(validated)

        return normalized_tags

    def to_dict(self) -> dict[str, object]:
        """Convert the contact to a serializable dictionary."""
        return {
            "contact_id": self.contact_id,
            "name": self.name,
            "phone_numbers": self.phone_numbers,
            "address": self.address,
            "email": self.email,
            "birthday": self.birthday,
            "note": self.note,
            "tags": self.tags,
            "created_at": self.created_at,
        }

    @classmethod
    def from_dict(cls, data: dict[str, object]) -> "Contact":
        """Create a contact instance from stored data."""
        raw_phone_numbers = data.get("phone_numbers", [])
        phone_values = raw_phone_numbers if isinstance(raw_phone_numbers, list) else []
        phone_numbers = [
            validate_phone(str(phone).strip())
            for phone in phone_values
            if str(phone).strip()
        ]

        if not phone_numbers:
            raise ValueError("Stored contact must contain at least one valid phone number")

        raw_tags = data.get("tags", [])
        tag_values = raw_tags if isinstance(raw_tags, list) else []
        tags = cls._normalize_tags([str(tag) for tag in tag_values])

        name = validate_name(str(data["name"]))
        address = validate_address(str(data["address"])) if data.get("address") else None
        email = validate_email(str(data["email"])) if data.get("email") else None
        birthday = validate_birthday(str(data["birthday"])) if data.get("birthday") else None
        note = cls._normalize_note(str(data["note"])) if data.get("note") is not None else None

        return cls(
            name=name,
            phone_numbers=phone_numbers,
            address=address,
            email=email,
            birthday=birthday,
            note=note,
            tags=tags,
            contact_id=str(data.get("contact_id", _generate_id())),
            created_at=str(data.get("created_at", _timestamp_now())),
        )

    def matches_search(self, query: str) -> bool:
        """Return True if the query matches any searchable contact field."""
        normalized_query = query.lower().strip()
        if not normalized_query:
            return False

        searchable_values = [
            self.name,
            self.email or "",
            self.address or "",
            self.note or "",
            *self.phone_numbers,
            *self.tags,
        ]
        return any(normalized_query in value.lower() for value in searchable_values)