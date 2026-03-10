"""Note domain model."""

from dataclasses import dataclass, field
from datetime import datetime
import uuid

from assistant_bot.utils.validators import (
    normalize_tag,
    validate_note_content,
    validate_tag,
)


@dataclass(slots=True)
class Note:
    """Represent a text note with optional tags."""

    content: str
    tags: list[str] = field(default_factory=list)
    note_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    created_at: str = field(default_factory=lambda: datetime.now().isoformat())
    updated_at: str = field(default_factory=lambda: datetime.now().isoformat())

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
            self.updated_at = datetime.now().isoformat()

    def add_tag(self, tag: str) -> None:
        """Add a validated tag to the note if it is not already present."""
        validated_tag = validate_tag(tag)
        if validated_tag not in self.tags:
            self.tags.append(validated_tag)
            self.updated_at = datetime.now().isoformat()

    def remove_tag(self, tag: str) -> None:
        """Remove a validated tag from the note if present."""
        validated_tag = validate_tag(tag)
        if validated_tag in self.tags:
            self.tags.remove(validated_tag)
            self.updated_at = datetime.now().isoformat()

    def to_dict(self) -> dict:
        """Convert the note to a serializable dictionary."""
        return {
            "note_id": self.note_id,
            "content": self.content,
            "tags": self.tags,
            "created_at": self.created_at,
            "updated_at": self.updated_at,
        }

    @classmethod
    def from_dict(cls, data: dict) -> "Note":
        """Create a note instance from stored data."""
        tags = cls._normalize_tags(data.get("tags", []))

        return cls(
            content=data["content"],
            tags=tags,
            note_id=data.get("note_id", str(uuid.uuid4())),
            created_at=data.get("created_at", datetime.now().isoformat()),
            updated_at=data.get("updated_at", datetime.now().isoformat()),
        )

    def matches_search(self, query: str) -> bool:
        """Return True if the query matches note content or tags."""
        query_lower = query.lower()
        return (
            query_lower in self.content.lower()
            or any(query_lower in tag for tag in self.tags)
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