"""JSON-based storage implementation."""

from __future__ import annotations

import json
import os
from collections.abc import Callable, Iterable
from pathlib import Path
from typing import TypeVar

from assistant_bot.domain.contacts import Contact
from assistant_bot.domain.exceptions import StorageError
from assistant_bot.domain.notes import Note
from assistant_bot.storage.base import BaseStorage
from assistant_bot.storage.paths import get_contacts_file, get_notes_file

T = TypeVar("T")

JSON_INDENT = 2
JSON_ENCODING = "utf-8"
BACKUP_SUFFIX = ".backup"
TEMP_SUFFIX = ".tmp"


class JSONStorage(BaseStorage):
    """JSON file-based storage for contacts and notes."""

    def __init__(self) -> None:
        """Initialize JSON storage paths."""
        self.contacts_file = get_contacts_file()
        self.notes_file = get_notes_file()
        self._ensure_storage_directories()

    def _ensure_storage_directories(self) -> None:
        """Ensure parent directories for storage files exist."""
        self.contacts_file.parent.mkdir(parents=True, exist_ok=True)
        self.notes_file.parent.mkdir(parents=True, exist_ok=True)

    def _create_backup(self, file_path: Path) -> None:
        """Create a non-destructive backup of an existing file."""
        if not file_path.exists():
            return

        backup_path = Path(f"{file_path}{BACKUP_SUFFIX}")
        counter = 1

        while backup_path.exists():
            backup_path = Path(f"{file_path}{BACKUP_SUFFIX}.{counter}")
            counter += 1

        try:
            file_path.rename(backup_path)
        except OSError:
            pass

    def _atomic_write(self, file_path: Path, data: object) -> None:
        """Write JSON data atomically to reduce corruption risk."""
        tmp_path = file_path.with_suffix(file_path.suffix + TEMP_SUFFIX)

        try:
            with tmp_path.open("w", encoding=JSON_ENCODING) as file:
                json.dump(data, file, indent=JSON_INDENT, ensure_ascii=False)
                file.flush()
                os.fsync(file.fileno())

            tmp_path.replace(file_path)
        finally:
            try:
                if tmp_path.exists():
                    tmp_path.unlink()
            except OSError:
                pass

    def _load_generic(
        self,
        file_path: Path,
        factory: Callable[[dict[str, object]], T],
    ) -> list[T]:
        """Load JSON data and convert dictionaries into domain objects."""
        if not file_path.exists():
            return []

        try:
            with file_path.open("r", encoding=JSON_ENCODING) as file:
                raw_data = json.load(file)

            if not isinstance(raw_data, list):
                self._create_backup(file_path)
                return []

            loaded_items: list[T] = []
            for item in raw_data:
                if not isinstance(item, dict):
                    self._create_backup(file_path)
                    return []

                loaded_items.append(factory(item))

            return loaded_items

        except json.JSONDecodeError:
            self._create_backup(file_path)
            return []
        except (KeyError, TypeError, ValueError):
            self._create_backup(file_path)
            return []

    def load_contacts(self) -> list[Contact]:
        """Load contacts from JSON storage."""
        try:
            return self._load_generic(self.contacts_file, Contact.from_dict)
        except OSError as error:
            raise StorageError(f"Failed to load contacts: {error}") from error

    def save_contacts(self, contacts: Iterable[Contact]) -> None:
        """Save contacts to JSON storage."""
        try:
            data = [contact.to_dict() for contact in contacts]
            self._atomic_write(self.contacts_file, data)
        except OSError as error:
            raise StorageError(f"Failed to save contacts: {error}") from error

    def load_notes(self) -> list[Note]:
        """Load notes from JSON storage."""
        try:
            return self._load_generic(self.notes_file, Note.from_dict)
        except OSError as error:
            raise StorageError(f"Failed to load notes: {error}") from error

    def save_notes(self, notes: Iterable[Note]) -> None:
        """Save notes to JSON storage."""
        try:
            data = [note.to_dict() for note in notes]
            self._atomic_write(self.notes_file, data)
        except OSError as error:
            raise StorageError(f"Failed to save notes: {error}") from error