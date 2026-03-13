"""Note domain model."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
import uuid

from assistant_bot.utils.validators import (
    normalize_tag,
    validate_note_content,
    validate_tag,
)


def _generate_id() -> str:
    """Return a new unique identifier."""
    return str(uuid.uuid4())


def _timestamp_now() -> str:
    """Return the current timestamp in ISO format."""
    return datetime.now().isoformat()


@dataclass(slots=True)
class Note:
    """Represent a text note with optional tags."""

    content: str
    tags: list[str] = field(default_factory=list)
    note_id: str = field(default_factory=_generate_id)
    created_at: str = field(default_factory=_timestamp_now)
    updated_at: str = field(default_factory=_timestamp_now)

    @classmethod
    def create(cls, content: str, tags: list[str] | None = None) -> "Note":
        """Create a validated note instance."""
        validated_content = validate_note_content(content)
        normalized_tags = cls._normalize_tags(tags or [])

        return cls(
            content=validated_content,
            tags=normalized_tags,
        )

    def update(self, content: str | None = None, tags: list[str] | None = None) -> None:
        """Update note content and/or tags with validation."""
        changed = False

        if content is not None:
            validated_content = validate_note_content(content)
            if validated_content != self.content:
                self.content = validated_content
                changed = True

        if tags is not None:
            normalized_tags = self._normalize_tags(tags)
            if normalized_tags != self.tags:
                self.tags = normalized_tags
                changed = True

        if changed:
            self.updated_at = _timestamp_now()

    def add_tag(self, tag: str) -> None:
        """Add a validated tag to the note if it is not already present."""
        validated_tag = validate_tag(tag)
        if validated_tag not in self.tags:
            self.tags.append(validated_tag)
            self.updated_at = _timestamp_now()

    def remove_tag(self, tag: str) -> None:
        """Remove a validated tag from the note if present."""
        validated_tag = validate_tag(tag)
        if validated_tag in self.tags:
            self.tags.remove(validated_tag)
            self.updated_at = _timestamp_now()

    def to_dict(self) -> dict[str, object]:
        """Convert the note to a serializable dictionary."""
        return {
            "note_id": self.note_id,
            "content": self.content,
            "tags": self.tags,
            "created_at": self.created_at,
            "updated_at": self.updated_at,
        }

    @classmethod
    def from_dict(cls, data: dict[str, object]) -> "Note":
        """Create a note instance from stored data."""
        raw_tags = data.get("tags", [])
        tag_values = raw_tags if isinstance(raw_tags, list) else []
        tags = cls._normalize_tags([str(tag) for tag in tag_values])

        return cls(
            content=validate_note_content(str(data["content"])),
            tags=tags,
            note_id=str(data.get("note_id", _generate_id())),
            created_at=str(data.get("created_at", _timestamp_now())),
            updated_at=str(data.get("updated_at", _timestamp_now())),
        )

    def matches_search(self, query: str) -> bool:
        """Return True if the query matches note content or tags."""
        normalized_query = query.lower()
        return (
            normalized_query in self.content.lower()
            or any(normalized_query in tag for tag in self.tags)
        )

    def has_tag(self, tag: str) -> bool:
        """Return True if the note contains the given normalized tag."""
        normalized = normalize_tag(tag)
        if not normalized:
            return False
        return normalized in self.tags

    def has_any_tag(self, tags: list[str]) -> bool:
        """Return True if the note contains at least one of the given tags."""
        return any(self.has_tag(tag) for tag in tags)

    def has_all_tags(self, tags: list[str]) -> bool:
        """Return True if the note contains all of the given tags."""
        return all(self.has_tag(tag) for tag in tags)

    def get_preview(self, max_length: int = 100) -> str:
        """Return a shortened preview of the note content."""
        if len(self.content) <= max_length:
            return self.content
        return self.content[: max_length - 3] + "..."

    @staticmethod
    def _normalize_tags(tags: list[str]) -> list[str]:
        """Validate, normalize, and deduplicate tags while preserving order."""
        normalized_tags: list[str] = []
        seen: set[str] = set()

        for tag in tags:
            validated_tag = validate_tag(tag)
            if validated_tag in seen:
                continue
            normalized_tags.append(validated_tag)
            seen.add(validated_tag)

        return normalized_tags