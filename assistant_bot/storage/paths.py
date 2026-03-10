"""Storage paths and configuration utilities."""

from __future__ import annotations

from pathlib import Path


DATA_DIR_NAME = "data"
CONTACTS_FILE_NAME = "contacts.json"
NOTES_FILE_NAME = "notes.json"


def get_project_root() -> Path:
    """Return the project root directory."""
    return Path(__file__).resolve().parents[2]


def get_data_dir() -> Path:
    """Return the project data directory and create it if needed."""
    data_dir = get_project_root() / DATA_DIR_NAME
    data_dir.mkdir(parents=True, exist_ok=True)
    return data_dir


def get_contacts_file() -> Path:
    """Return the path to the contacts JSON file."""
    return get_data_dir() / CONTACTS_FILE_NAME


def get_notes_file() -> Path:
    """Return the path to the notes JSON file."""
    return get_data_dir() / NOTES_FILE_NAME