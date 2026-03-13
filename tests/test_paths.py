import pytest
from pathlib import Path

from assistant_bot.storage import paths


class TestPathConstants:
    """Tests for path configuration constants."""

    def test_data_dir_name_constant(self):
        """DATA_DIR_NAME should be defined."""
        assert paths.DATA_DIR_NAME == "data"

    def test_contacts_file_name_constant(self):
        """CONTACTS_FILE_NAME should be defined."""
        assert paths.CONTACTS_FILE_NAME == "contacts.json"

    def test_notes_file_name_constant(self):
        """NOTES_FILE_NAME should be defined."""
        assert paths.NOTES_FILE_NAME == "notes.json"


class TestGetProjectRoot:
    """Tests for get_project_root function."""

    def test_get_project_root_returns_path(self):
        """Should return a Path object."""
        root = paths.get_project_root()
        assert isinstance(root, Path)

    def test_get_project_root_is_absolute(self):
        """Project root should be an absolute path."""
        root = paths.get_project_root()
        assert root.is_absolute()

    def test_get_project_root_is_valid_directory(self):
        """Project root should be a valid directory."""
        root = paths.get_project_root()
        assert root.exists()
        assert root.is_dir()

    def test_get_project_root_contains_assistant_bot(self):
        """Project root should contain assistant_bot directory."""
        root = paths.get_project_root()
        assert (root / "assistant_bot").exists()
        assert (root / "assistant_bot").is_dir()

    def test_get_project_root_consistency(self):
        """Repeated calls should return same path."""
        root1 = paths.get_project_root()
        root2 = paths.get_project_root()
        assert root1 == root2


class TestGetDataDir:
    """Tests for get_data_dir function."""

    def test_get_data_dir_returns_path(self):
        """Should return a Path object."""
        data_dir = paths.get_data_dir()
        assert isinstance(data_dir, Path)

    def test_get_data_dir_is_absolute(self):
        """Data directory path should be absolute."""
        data_dir = paths.get_data_dir()
        assert data_dir.is_absolute()

    def test_get_data_dir_creates_directory(self, tmp_path, monkeypatch):
        """Should create directory if it doesn't exist."""
        monkeypatch.setattr(paths, "get_project_root", lambda: tmp_path)
        # Verify no data dir exists yet
        data_dir = tmp_path / "data"
        assert not data_dir.exists()

        # Call get_data_dir - should create it
        result = paths.get_data_dir()
        assert result.exists()
        assert result.is_dir()

    def test_get_data_dir_handles_existing_directory(
        self, tmp_path, monkeypatch
    ):
        """Should not fail if directory already exists."""
        monkeypatch.setattr(paths, "get_project_root", lambda: tmp_path)
        data_dir = tmp_path / "data"
        data_dir.mkdir()

        # Call should succeed
        result = paths.get_data_dir()
        assert result.exists()
        assert result == data_dir

    def test_get_data_dir_creates_parent_dirs(self, tmp_path, monkeypatch):
        """Should create parent directories if needed."""
        monkeypatch.setattr(paths, "get_project_root", lambda: tmp_path)
        # get_data_dir with parents=True should handle anything
        result = paths.get_data_dir()
        assert result.exists()
        assert result.parent.exists()

    def test_get_data_dir_consistency(self, tmp_path, monkeypatch):
        """Repeated calls should return same path."""
        monkeypatch.setattr(paths, "get_project_root", lambda: tmp_path)
        dir1 = paths.get_data_dir()
        dir2 = paths.get_data_dir()
        assert dir1 == dir2

    def test_get_data_dir_name_in_path(self, tmp_path, monkeypatch):
        """Data directory name should be 'data'."""
        monkeypatch.setattr(paths, "get_project_root", lambda: tmp_path)
        data_dir = paths.get_data_dir()
        assert data_dir.name == "data"

    def test_get_data_dir_under_project_root(self, tmp_path, monkeypatch):
        """Data dir should be a child of project root."""
        monkeypatch.setattr(paths, "get_project_root", lambda: tmp_path)
        data_dir = paths.get_data_dir()
        assert data_dir.parent == tmp_path


class TestGetContactsFile:
    """Tests for get_contacts_file function."""

    def test_get_contacts_file_returns_path(self, tmp_path, monkeypatch):
        """Should return a Path object."""
        monkeypatch.setattr(paths, "get_project_root", lambda: tmp_path)
        contacts_file = paths.get_contacts_file()
        assert isinstance(contacts_file, Path)

    def test_get_contacts_file_is_absolute(self, tmp_path, monkeypatch):
        """Contacts file path should be absolute."""
        monkeypatch.setattr(paths, "get_project_root", lambda: tmp_path)
        contacts_file = paths.get_contacts_file()
        assert contacts_file.is_absolute()

    def test_get_contacts_file_name(self, tmp_path, monkeypatch):
        """Contacts file should be named 'contacts.json'."""
        monkeypatch.setattr(paths, "get_project_root", lambda: tmp_path)
        contacts_file = paths.get_contacts_file()
        assert contacts_file.name == "contacts.json"

    def test_get_contacts_file_in_data_dir(self, tmp_path, monkeypatch):
        """Contacts file should be in data directory."""
        monkeypatch.setattr(paths, "get_project_root", lambda: tmp_path)
        contacts_file = paths.get_contacts_file()
        data_dir = paths.get_data_dir()
        assert contacts_file.parent == data_dir

    def test_get_contacts_file_suffix(self, tmp_path, monkeypatch):
        """Contacts file should have .json suffix."""
        monkeypatch.setattr(paths, "get_project_root", lambda: tmp_path)
        contacts_file = paths.get_contacts_file()
        assert contacts_file.suffix == ".json"

    def test_get_contacts_file_consistency(self, tmp_path, monkeypatch):
        """Repeated calls should return same path."""
        monkeypatch.setattr(paths, "get_project_root", lambda: tmp_path)
        file1 = paths.get_contacts_file()
        file2 = paths.get_contacts_file()
        assert file1 == file2


class TestGetNotesFile:
    """Tests for get_notes_file function."""

    def test_get_notes_file_returns_path(self, tmp_path, monkeypatch):
        """Should return a Path object."""
        monkeypatch.setattr(paths, "get_project_root", lambda: tmp_path)
        notes_file = paths.get_notes_file()
        assert isinstance(notes_file, Path)

    def test_get_notes_file_is_absolute(self, tmp_path, monkeypatch):
        """Notes file path should be absolute."""
        monkeypatch.setattr(paths, "get_project_root", lambda: tmp_path)
        notes_file = paths.get_notes_file()
        assert notes_file.is_absolute()

    def test_get_notes_file_name(self, tmp_path, monkeypatch):
        """Notes file should be named 'notes.json'."""
        monkeypatch.setattr(paths, "get_project_root", lambda: tmp_path)
        notes_file = paths.get_notes_file()
        assert notes_file.name == "notes.json"

    def test_get_notes_file_in_data_dir(self, tmp_path, monkeypatch):
        """Notes file should be in data directory."""
        monkeypatch.setattr(paths, "get_project_root", lambda: tmp_path)
        notes_file = paths.get_notes_file()
        data_dir = paths.get_data_dir()
        assert notes_file.parent == data_dir

    def test_get_notes_file_suffix(self, tmp_path, monkeypatch):
        """Notes file should have .json suffix."""
        monkeypatch.setattr(paths, "get_project_root", lambda: tmp_path)
        notes_file = paths.get_notes_file()
        assert notes_file.suffix == ".json"

    def test_get_notes_file_consistency(self, tmp_path, monkeypatch):
        """Repeated calls should return same path."""
        monkeypatch.setattr(paths, "get_project_root", lambda: tmp_path)
        file1 = paths.get_notes_file()
        file2 = paths.get_notes_file()
        assert file1 == file2


class TestFilePathRelationships:
    """Tests for relationships between paths."""

    def test_contacts_and_notes_in_same_directory(
        self, tmp_path, monkeypatch
    ):
        """Both files should be in the same data directory."""
        monkeypatch.setattr(paths, "get_project_root", lambda: tmp_path)
        contacts = paths.get_contacts_file()
        notes = paths.get_notes_file()
        assert contacts.parent == notes.parent

    def test_files_are_different_paths(self, tmp_path, monkeypatch):
        """Contacts and notes files should be different paths."""
        monkeypatch.setattr(paths, "get_project_root", lambda: tmp_path)
        contacts = paths.get_contacts_file()
        notes = paths.get_notes_file()
        assert contacts != notes

    def test_data_dir_contains_json_files(self, tmp_path, monkeypatch):
        """Data directory should contain the JSON files."""
        monkeypatch.setattr(paths, "get_project_root", lambda: tmp_path)
        data_dir = paths.get_data_dir()
        contacts = paths.get_contacts_file()
        notes = paths.get_notes_file()

        assert str(contacts).startswith(str(data_dir))
        assert str(notes).startswith(str(data_dir))
