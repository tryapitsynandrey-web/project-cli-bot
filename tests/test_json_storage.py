import json
from pathlib import Path

import pytest

from assistant_bot.storage.json_storage import JSONStorage
from assistant_bot.domain.contacts import Contact
from assistant_bot.domain.notes import Note
from assistant_bot.domain.exceptions import StorageError


class TestJSONStorageSaveContacts:
    """Tests for saving contacts to JSON storage."""

    def test_save_single_contact(self, tmp_data_dir):
        """Should save a single contact to JSON file."""
        storage = JSONStorage()
        contact = Contact.create(
            name="Alice Adams",
            phone_numbers=["+353830000001"]
        )
        storage.save_contacts([contact])

        # Verify file exists and contains data
        assert storage.contacts_file.exists()
        data = json.loads(storage.contacts_file.read_text())
        assert len(data) == 1
        assert data[0]["name"] == "Alice Adams"

    def test_save_multiple_contacts(self, tmp_data_dir):
        """Should save multiple contacts."""
        storage = JSONStorage()
        contacts = [
            Contact.create(name="Bob Baker", phone_numbers=["+353830000002"]),
            Contact.create(name="Carol Chen", phone_numbers=["+353830000003"]),
            Contact.create(name="David Davis", phone_numbers=["+353830000004"]),
        ]
        storage.save_contacts(contacts)

        data = json.loads(storage.contacts_file.read_text())
        assert len(data) == 3
        assert data[0]["name"] == "Bob Baker"
        assert data[1]["name"] == "Carol Chen"
        assert data[2]["name"] == "David Davis"

    def test_save_empty_contact_list(self, tmp_data_dir):
        """Should handle saving empty contact list."""
        storage = JSONStorage()
        storage.save_contacts([])

        assert storage.contacts_file.exists()
        data = json.loads(storage.contacts_file.read_text())
        assert data == []

    def test_save_overwrites_previous(self, tmp_data_dir):
        """Saving should overwrite previous data."""
        storage = JSONStorage()
        
        # Save first batch
        contact1 = Contact.create(name="First", phone_numbers=["+353830000005"])
        storage.save_contacts([contact1])
        
        # Save second batch - should replace
        contact2 = Contact.create(name="Second", phone_numbers=["+353830000006"])
        storage.save_contacts([contact2])

        data = json.loads(storage.contacts_file.read_text())
        assert len(data) == 1
        assert data[0]["name"] == "Second"

    def test_save_preserves_contact_fields(self, tmp_data_dir):
        """Saved contact should have all fields."""
        storage = JSONStorage()
        contact = Contact.create(
            name="Emma Elliot",
            phone_numbers=["+353830000007", "+353830000008"],
            email="emma@test.co.uk",
            address="123 Main St",
            birthday="1990-05-10",
            note="Important client",
            tags=["work", "priority"]
        )
        storage.save_contacts([contact])

        data = json.loads(storage.contacts_file.read_text())
        saved = data[0]
        assert saved["name"] == "Emma Elliot"
        assert len(saved["phone_numbers"]) == 2
        assert saved["email"] == "emma@test.co.uk"
        assert saved["address"] == "123 Main St"
        assert saved["birthday"] == "1990-05-10"
        assert saved["note"] == "Important client"


class TestJSONStorageLoadContacts:
    """Tests for loading contacts from JSON storage."""

    def test_load_contacts_from_saved_file(self, tmp_data_dir):
        """Should load contacts that were saved."""
        storage = JSONStorage()
        original = Contact.create(
            name="Frank Foster",
            phone_numbers=["+353830000009"]
        )
        storage.save_contacts([original])

        loaded = storage.load_contacts()
        assert len(loaded) == 1
        assert isinstance(loaded[0], Contact)
        assert loaded[0].name == "Frank Foster"

    def test_load_contacts_returns_domain_objects(self, tmp_data_dir):
        """Load should return Contact domain objects, not dicts."""
        storage = JSONStorage()
        contact = Contact.create(name="Gail Green", phone_numbers=["+353830000010"])
        storage.save_contacts([contact])

        loaded = storage.load_contacts()
        assert isinstance(loaded[0], Contact)
        assert hasattr(loaded[0], 'name')
        assert hasattr(loaded[0], 'phone_numbers')

    def test_load_empty_file_returns_empty_list(self, tmp_data_dir):
        """Loading from empty file should return empty list."""
        storage = JSONStorage()
        storage.save_contacts([])

        loaded = storage.load_contacts()
        assert loaded == []

    def test_load_nonexistent_file_returns_empty_list(self, tmp_data_dir):
        """Loading when no file exists should return empty list."""
        storage = JSONStorage()
        # Don't save anything - file won't exist
        if storage.contacts_file.exists():
            storage.contacts_file.unlink()

        loaded = storage.load_contacts()
        assert loaded == []

    def test_load_multiple_contacts(self, tmp_data_dir):
        """Should load all saved contacts."""
        storage = JSONStorage()
        contacts = [
            Contact.create(name="Hannah Harris", phone_numbers=["+353830000011"]),
            Contact.create(name="Isaac Ingles", phone_numbers=["+353830000012"]),
            Contact.create(name="Julia Jackson", phone_numbers=["+353830000013"]),
        ]
        storage.save_contacts(contacts)

        loaded = storage.load_contacts()
        assert len(loaded) == 3
        assert loaded[0].name == "Hannah Harris"
        assert loaded[1].name == "Isaac Ingles"
        assert loaded[2].name == "Julia Jackson"

    def test_load_preserves_all_fields(self, tmp_data_dir):
        """Loaded contact should preserve all fields."""
        storage = JSONStorage()
        original = Contact.create(
            name="Kevin King",
            phone_numbers=["+353830000014"],
            email="kevin@test.co.uk",
            address="42 Oak Ave",
            birthday="1985-03-25",
            note="VIP client",
            tags=["partner", "old"]
        )
        storage.save_contacts([original])

        loaded = storage.load_contacts()[0]
        assert loaded.name == "Kevin King"
        assert loaded.email == "kevin@test.co.uk"
        assert loaded.address == "42 Oak Ave"
        assert loaded.birthday == "1985-03-25"
        assert loaded.note == "VIP client"
        assert "partner" in loaded.tags


class TestJSONStorageSaveNotes:
    """Tests for saving notes to JSON storage."""

    def test_save_single_note(self, tmp_data_dir):
        """Should save a single note to JSON file."""
        storage = JSONStorage()
        note = Note.create(content="First note")
        storage.save_notes([note])

        assert storage.notes_file.exists()
        data = json.loads(storage.notes_file.read_text())
        assert len(data) == 1
        assert data[0]["content"] == "First note"

    def test_save_multiple_notes(self, tmp_data_dir):
        """Should save multiple notes."""
        storage = JSONStorage()
        notes = [
            Note.create(content="Note one"),
            Note.create(content="Note two"),
            Note.create(content="Note three"),
        ]
        storage.save_notes(notes)

        data = json.loads(storage.notes_file.read_text())
        assert len(data) == 3

    def test_save_empty_note_list(self, tmp_data_dir):
        """Should handle empty note list."""
        storage = JSONStorage()
        storage.save_notes([])

        assert storage.notes_file.exists()
        data = json.loads(storage.notes_file.read_text())
        assert data == []

    def test_save_notes_with_tags(self, tmp_data_dir):
        """Should preserve note tags."""
        storage = JSONStorage()
        note = Note.create(
            content="Tagged note",
            tags=["work", "important"]
        )
        storage.save_notes([note])

        data = json.loads(storage.notes_file.read_text())
        assert "work" in data[0]["tags"]
        assert "important" in data[0]["tags"]


class TestJSONStorageLoadNotes:
    """Tests for loading notes from JSON storage."""

    def test_load_notes_from_saved_file(self, tmp_data_dir):
        """Should load notes that were saved."""
        storage = JSONStorage()
        original = Note.create(content="Saved note")
        storage.save_notes([original])

        loaded = storage.load_notes()
        assert len(loaded) == 1
        assert isinstance(loaded[0], Note)
        assert loaded[0].content == "Saved note"

    def test_load_notes_returns_domain_objects(self, tmp_data_dir):
        """Load should return Note domain objects."""
        storage = JSONStorage()
        note = Note.create(content="Domain object test")
        storage.save_notes([note])

        loaded = storage.load_notes()
        assert isinstance(loaded[0], Note)
        assert hasattr(loaded[0], 'content')

    def test_load_empty_notes_file_returns_empty_list(self, tmp_data_dir):
        """Loading empty notes file should return empty list."""
        storage = JSONStorage()
        storage.save_notes([])

        loaded = storage.load_notes()
        assert loaded == []

    def test_load_nonexistent_notes_file_returns_empty_list(self, tmp_data_dir):
        """Loading when no notes file exists should return empty list."""
        storage = JSONStorage()
        if storage.notes_file.exists():
            storage.notes_file.unlink()

        loaded = storage.load_notes()
        assert loaded == []


class TestJSONStorageCorruptionHandling:
    """Tests for handling corrupted JSON files."""

    def test_corrupted_contacts_file_creates_backup(self, tmp_data_dir):
        """Corrupted contacts file should create backup and return empty list."""
        storage = JSONStorage()
        # Write invalid JSON
        storage.contacts_file.write_text("not-valid-json{{{")
        
        loaded = storage.load_contacts()
        
        # Should return empty list
        assert loaded == []
        # Should create backup
        backups = list(storage.contacts_file.parent.glob(storage.contacts_file.name + ".backup*"))
        assert len(backups) > 0

    def test_corrupted_notes_file_creates_backup(self, tmp_data_dir):
        """Corrupted notes file should create backup and return empty list."""
        storage = JSONStorage()
        # Write invalid JSON
        storage.notes_file.write_text("[not-json{{{")
        
        loaded = storage.load_notes()
        
        # Should return empty list
        assert loaded == []
        # Should create backup
        backups = list(storage.notes_file.parent.glob(storage.notes_file.name + ".backup*"))
        assert len(backups) > 0

    def test_non_list_json_creates_backup(self, tmp_data_dir):
        """JSON file with non-list data should create backup."""
        storage = JSONStorage()
        # Write valid JSON but not a list
        storage.contacts_file.write_text('{"key": "value"}')
        
        loaded = storage.load_contacts()
        
        assert loaded == []
        backups = list(storage.contacts_file.parent.glob(storage.contacts_file.name + ".backup*"))
        assert len(backups) > 0

    def test_list_with_non_dict_items_creates_backup(self, tmp_data_dir):
        """JSON file with list of non-dicts should create backup."""
        storage = JSONStorage()
        # Write valid JSON list but items aren't dicts
        storage.contacts_file.write_text('["string", 123, null]')
        
        loaded = storage.load_contacts()
        
        assert loaded == []
        backups = list(storage.contacts_file.parent.glob(storage.contacts_file.name + ".backup*"))
        assert len(backups) > 0

    def test_multiple_backup_files_incremented(self, tmp_data_dir):
        """Multiple corruptions should create incrementally named backups."""
        storage = JSONStorage()
        
        # First corruption
        storage.contacts_file.write_text("{bad")
        storage.load_contacts()
        
        # Create file again and corrupt again
        storage.contacts_file.write_text("{{bad)")
        storage.load_contacts()
        
        # Should have multiple backups
        backups = list(storage.contacts_file.parent.glob(storage.contacts_file.name + ".backup*"))
        assert len(backups) >= 2


class TestJSONStorageRoundtrip:
    """Tests for save/load roundtrip integrity."""

    def test_contact_roundtrip_preserves_data(self, tmp_data_dir):
        """Contact data should survive save/load cycle."""
        storage = JSONStorage()
        original = Contact.create(
            name="Leo Laurel",
            phone_numbers=["+353830000015", "+353830000016"],
            email="leo@test.co.uk",
            address="999 Pine Rd",
            birthday="1995-11-20",
            note="Great contact",
            tags=["vip"]
        )
        original_id = original.contact_id
        
        storage.save_contacts([original])
        loaded = storage.load_contacts()[0]
        
        assert loaded.name == original.name
        assert loaded.phone_numbers == original.phone_numbers
        assert loaded.email == original.email
        assert loaded.address == original.address
        assert loaded.birthday == original.birthday
        assert loaded.note == original.note
        assert loaded.contact_id == original_id

    def test_note_roundtrip_preserves_data(self, tmp_data_dir):
        """Note data should survive save/load cycle."""
        storage = JSONStorage()
        original = Note.create(
            content="Important information stored here",
            tags=["critical", "archive"]
        )
        original_id = original.note_id
        
        storage.save_notes([original])
        loaded = storage.load_notes()[0]
        
        assert loaded.content == original.content
        assert set(loaded.tags) == set(original.tags)
        assert loaded.note_id == original_id

    def test_multiple_save_load_cycles(self, tmp_data_dir):
        """Repeated cycles should maintain data integrity."""
        storage = JSONStorage()
        
        # Save batch 1
        batch1 = [Contact.create(name="Mike Martin", phone_numbers=["+353830000017"])]
        storage.save_contacts(batch1)
        
        # Load and modify
        loaded1 = storage.load_contacts()
        assert len(loaded1) == 1
        
        # Save batch 2 (replaces)
        batch2 = [
            Contact.create(name="Nina Nelson", phone_numbers=["+353830000018"]),
            Contact.create(name="Oscar Olson", phone_numbers=["+353830000019"]),
        ]
        storage.save_contacts(batch2)
        
        # Load both
        loaded2 = storage.load_contacts()
        assert len(loaded2) == 2
        assert loaded2[0].name == "Nina Nelson"
        assert loaded2[1].name == "Oscar Olson"


class TestJSONStorageInitialization:
    """Tests for storage initialization."""

    def test_storage_creates_data_directory(self, tmp_path, monkeypatch):
        """Storage should create data directory if it doesn't exist."""
        monkeypatch.setattr("assistant_bot.storage.json_storage.get_contacts_file", 
                          lambda: tmp_path / "data" / "contacts.json")
        monkeypatch.setattr("assistant_bot.storage.json_storage.get_notes_file",
                          lambda: tmp_path / "data" / "notes.json")
        
        # Verify directory doesn't exist yet
        data_dir = tmp_path / "data"
        assert not data_dir.exists()
        
        # Create storage - should create directory
        storage = JSONStorage()
        assert data_dir.exists()
        assert storage.contacts_file.parent.exists()

    def test_storage_paths_are_absolute(self, tmp_data_dir):
        """Storage file paths should be absolute."""
        storage = JSONStorage()
        assert storage.contacts_file.is_absolute()
        assert storage.notes_file.is_absolute()

    def test_storage_handles_existing_directory(self, tmp_data_dir):
        """Storage should not fail if directory already exists."""
        storage = JSONStorage()
        # Should not raise even if directory exists
        assert storage.contacts_file.parent.exists()
        assert storage.notes_file.parent.exists()
