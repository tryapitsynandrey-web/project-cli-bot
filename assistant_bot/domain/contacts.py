"""Contact domain model."""

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
    contact_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    created_at: str = field(default_factory=lambda: datetime.now().isoformat())

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
        validated_phones = [validate_phone(phone) for phone in phone_numbers if phone]

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
            validated_phones = [validate_phone(phone) for phone in phone_numbers if phone]
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

        updated_tags = []
        for tag in self.tags:
            if tag == old_normalized:
                updated_tags.append(validated_new_tag)
            else:
                updated_tags.append(tag)

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

    def to_dict(self) -> dict:
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
    def from_dict(cls, data: dict) -> "Contact":
        """Create a contact instance from stored data."""
        raw_phone_numbers = data.get("phone_numbers", [])
        phone_numbers = [
            validate_phone(str(phone).strip())
            for phone in raw_phone_numbers
            if str(phone).strip()
        ]

        if not phone_numbers:
            raise ValueError("Stored contact must contain at least one valid phone number")

        name = validate_name(data["name"])
        address = validate_address(data["address"]) if data.get("address") else None
        email = validate_email(data["email"]) if data.get("email") else None
        birthday = validate_birthday(data["birthday"]) if data.get("birthday") else None
        note = cls._normalize_note(data.get("note"))
        tags = cls._normalize_tags(data.get("tags", []))

        return cls(
            name=name,
            phone_numbers=phone_numbers,
            address=address,
            email=email,
            birthday=birthday,
            note=note,
            tags=tags,
            contact_id=data.get("contact_id", str(uuid.uuid4())),
            created_at=data.get("created_at", datetime.now().isoformat()),
        )

    def matches_search(self, query: str) -> bool:
        """Return True if the query matches any searchable contact field."""
        query_lower = query.lower().strip()
        if not query_lower:
            return False

        return (
            query_lower in self.name.lower()
            or (self.email is not None and query_lower in self.email.lower())
            or (self.address is not None and query_lower in self.address.lower())
            or (self.note is not None and query_lower in self.note.lower())
            or any(query_lower in phone.lower() for phone in self.phone_numbers)
            or any(query_lower in tag.lower() for tag in self.tags)
        )