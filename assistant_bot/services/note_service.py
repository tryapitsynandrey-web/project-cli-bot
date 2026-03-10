"""Note management service."""

from assistant_bot.domain.exceptions import NoteNotFoundError
from assistant_bot.domain.notes import Note
from assistant_bot.storage.base import BaseStorage


class NoteService:
    """Service for managing notes."""

    def __init__(self, storage: BaseStorage) -> None:
        """Initialize the note service."""
        self.storage = storage
        self.notes: list[Note] = []
        self._load()

    def _load(self) -> None:
        """Load notes from storage."""
        self.notes = self.storage.load_notes()

    def _save(self) -> None:
        """Persist notes to storage."""
        self.storage.save_notes(self.notes)

    @staticmethod
    def _sort_by_created(notes: list[Note], descending: bool = True) -> list[Note]:
        """Return notes sorted by creation time."""
        return sorted(notes, key=lambda note: note.created_at, reverse=descending)

    def add_note(self, content: str, tags: list[str] | None = None) -> Note:
        """Create and store a new note."""
        note = Note.create(content=content, tags=tags or [])
        self.notes.append(note)
        self._save()
        return note

    def get_note(self, note_id: str) -> Note:
        """Return a note by ID."""
        for note in self.notes:
            if note.note_id == note_id:
                return note
        raise NoteNotFoundError(f"Note {note_id} not found")

    def get_all_notes(self) -> list[Note]:
        """Return all notes sorted by creation time, newest first."""
        return self._sort_by_created(self.notes)

    def get_notes_sorted_by_tags(self, descending: bool = True) -> list[Note]:
        """Return notes sorted by number of tags."""
        return sorted(self.notes, key=lambda note: len(note.tags), reverse=descending)

    def get_notes_sorted_by_updated(self, descending: bool = True) -> list[Note]:
        """Return notes sorted by last update time."""
        return sorted(self.notes, key=lambda note: note.updated_at, reverse=descending)

    def update_note(
        self,
        note_id: str,
        content: str | None = None,
        tags: list[str] | None = None,
    ) -> Note:
        """Update a note and persist the changes."""
        note = self.get_note(note_id)
        note.update(content=content, tags=tags)
        self._save()
        return note

    def delete_note(self, note_id: str) -> None:
        """Delete a note by ID."""
        note = self.get_note(note_id)
        self.notes.remove(note)
        self._save()

    def search_notes(self, query: str) -> list[Note]:
        """Search notes by content or tags."""
        results = [note for note in self.notes if note.matches_search(query)]
        return self._sort_by_created(results)

    def get_notes_by_tag(self, tag: str) -> list[Note]:
        """Return notes that contain the given tag."""
        results = [note for note in self.notes if note.has_tag(tag)]
        return self._sort_by_created(results)

    def get_notes_by_any_tag(self, tags: list[str]) -> list[Note]:
        """Return notes that contain at least one of the given tags."""
        results = [note for note in self.notes if note.has_any_tag(tags)]
        return self._sort_by_created(results)

    def get_notes_by_all_tags(self, tags: list[str]) -> list[Note]:
        """Return notes that contain all of the given tags."""
        results = [note for note in self.notes if note.has_all_tags(tags)]
        return self._sort_by_created(results)

    def get_all_tags(self) -> set[str]:
        """Return all unique tags used across notes."""
        all_tags: set[str] = set()
        for note in self.notes:
            all_tags.update(note.tags)
        return all_tags