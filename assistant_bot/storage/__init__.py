"""Storage package exports."""

from assistant_bot.storage.base import BaseStorage
from assistant_bot.storage.json_storage import JSONStorage
from assistant_bot.storage.paths import get_contacts_file, get_data_dir, get_notes_file

__all__ = [
    "BaseStorage",
    "JSONStorage",
    "get_contacts_file",
    "get_data_dir",
    "get_notes_file",
]