"""Storage paths and configuration utilities."""

from __future__ import annotations

from pathlib import Path


APP_DIR_NAME = ".assistant_bot"
DATA_DIR_NAME = "data"
CONTACTS_FILE_NAME = "contacts.json"
NOTES_FILE_NAME = "notes.json"


def get_app_dir() -> Path:
    """Return the application directory inside the user's home directory."""
    app_dir = Path.home() / APP_DIR_NAME
    app_dir.mkdir(parents=True, exist_ok=True)
    return app_dir


def get_data_dir() -> Path:
    """Return the data storage directory and create it if needed."""
    data_dir = get_app_dir() / DATA_DIR_NAME
    data_dir.mkdir(parents=True, exist_ok=True)
    return data_dir


def get_contacts_file() -> Path:
    """Return the path to the contacts JSON file."""
    return get_data_dir() / CONTACTS_FILE_NAME


def get_notes_file() -> Path:
    """Return the path to the notes JSON file."""
    return get_data_dir() / NOTES_FILE_NAME