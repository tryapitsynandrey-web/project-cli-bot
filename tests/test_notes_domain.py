import pytest
from datetime import datetime

from assistant_bot.domain.notes import Note


class TestNoteCreation:
    """Tests for note creation and initialization."""

    def test_create_note_with_required_fields(self):
        """Should create note with content only."""
        note = Note.create(content="This is a note")
        assert note.content == "This is a note"
        assert note.tags == []

    def test_create_note_with_tags(self):
        """Should create note with content and tags."""
        note = Note.create(
            content="Tagged note",
            tags=["personal", "important"]
        )
        assert note.content == "Tagged note"
        assert "personal" in note.tags
        assert "important" in note.tags

    def test_create_note_generates_id(self):
        """Should generate note_id if not provided."""
        note = Note.create(content="Test")
        assert note.note_id
        assert len(note.note_id) > 0

    def test_create_note_sets_timestamps(self):
        """Should set created_at and updated_at on creation."""
        note = Note.create(content="Timestamped note")
        assert note.created_at
        assert note.updated_at
        assert "T" in note.created_at  # ISO format
        assert "T" in note.updated_at

    def test_create_note_with_empty_tags(self):
        """Should handle empty tag list."""
        note = Note.create(content="No tags", tags=[])
        assert note.tags == []

    def test_create_note_tags_normalized(self):
        """Tags should be normalized (lowercase) on creation."""
        note = Note.create(
            content="Normalized",
            tags=["Work", "URGENT", "personal"]
        )
        # All should be lowercase and deduplicated
        assert "work" in note.tags
        assert "urgent" in note.tags

    def test_create_note_tags_deduplicated(self):
        """Tags should be deduplicated on creation."""
        note = Note.create(
            content="Deduplicated",
            tags=["tag", "TAG", "Tag"]
        )
        # Should have only one "tag" entry
        assert note.tags.count("tag") == 1

    def test_create_note_very_long_content(self):
        """Should handle very long note content within limits."""
        long_content = "x" * 9999  # Near but under max of 10000
        note = Note.create(content=long_content)
        assert len(note.content) == 9999

    def test_create_note_with_special_characters(self):
        """Should handle special characters in content."""
        content = "Note with emoji 🎉 and symbols @#$%"
        note = Note.create(content=content)
        assert "🎉" in note.content
        assert "@#$%" in note.content

    def test_create_note_with_newlines(self):
        """Newlines in content should be normalized to spaces."""
        content = "Line 1\nLine 2\nLine 3"
        note = Note.create(content=content)
        # Newlines are normalized to spaces in content
        assert "\n" not in note.content
        assert "Line 1" in note.content
        assert "Line 2" in note.content
        assert "Line 3" in note.content


class TestNoteSerialization:
    """Tests for to_dict and from_dict methods."""

    def test_to_dict_contains_all_fields(self):
        """to_dict should include all note fields."""
        note = Note.create(content="Serialized", tags=["aa"])
        d = note.to_dict()
        assert "note_id" in d
        assert "content" in d
        assert "tags" in d
        assert "created_at" in d
        assert "updated_at" in d

    def test_to_dict_preserves_values(self):
        """to_dict values should match note fields."""
        note = Note.create(content="Test content", tags=["test"])
        d = note.to_dict()
        assert d["content"] == "Test content"
        assert "test" in d["tags"]
        assert d["note_id"] == note.note_id

    def test_from_dict_restores_all_fields(self):
        """from_dict should restore all note data."""
        original = {
            "note_id": "test-id-456",
            "content": "Restored note",
            "tags": ["restored", "old"],
            "created_at": "2024-01-01T10:00:00",
            "updated_at": "2024-01-02T10:00:00"
        }
        note = Note.from_dict(original)
        assert note.note_id == "test-id-456"
        assert note.content == "Restored note"
        assert "restored" in note.tags
        assert note.created_at == "2024-01-01T10:00:00"
        assert note.updated_at == "2024-01-02T10:00:00"

    def test_roundtrip_create_to_dict_from_dict(self):
        """Note should round-trip through to_dict and from_dict."""
        original = Note.create(
            content="Round-trip test",
            tags=["one", "two", "three"]
        )
        original_id = original.note_id
        original_created = original.created_at

        # Serialize and deserialize
        dict_repr = original.to_dict()
        restored = Note.from_dict(dict_repr)

        assert restored.content == original.content
        assert set(restored.tags) == set(original.tags)
        assert restored.note_id == original_id
        assert restored.created_at == original_created

    def test_from_dict_with_minimal_data(self):
        """from_dict should work with minimal required data."""
        data = {"content": "Minimal"}
        note = Note.from_dict(data)
        assert note.content == "Minimal"
        assert note.tags == []
        assert note.note_id  # Should generate ID

    def test_from_dict_missing_tags_defaults_to_empty(self):
        """from_dict should default tags to empty list if missing."""
        data = {"content": "No tags provided"}
        note = Note.from_dict(data)
        assert note.tags == []


class TestNoteUpdate:
    """Tests for updating note content and tags."""

    def test_update_content(self):
        """Should update content field."""
        note = Note.create(content="Original")
        original_created = note.created_at
        note.update(content="Updated")
        assert note.content == "Updated"
        assert note.updated_at != original_created

    def test_update_tags(self):
        """Should update tags field."""
        note = Note.create(content="Content", tags=["old"])
        original_created = note.created_at
        note.update(tags=["new", "updated"])
        assert "old" not in note.tags
        assert "new" in note.tags
        assert "updated" in note.tags
        assert note.updated_at != original_created

    def test_update_both_content_and_tags(self):
        """Should update both content and tags."""
        note = Note.create(content="Old content", tags=["old"])
        note.update(content="New content", tags=["new"])
        assert note.content == "New content"
        assert "new" in note.tags
        assert "old" not in note.tags

    def test_update_with_none_leaves_unchanged(self):
        """Passing None should not change that field."""
        note = Note.create(content="Content", tags=["tag"])
        original_content = note.content
        note.update(content=None, tags=None)
        assert note.content == original_content
        assert "tag" in note.tags
        # updated_at is always updated on any update() call
        assert note.updated_at >= note.created_at

    def test_update_no_change_preserves_timestamp(self):
        """If content doesn't actually change, updated_at shouldn't change."""
        note = Note.create(content="Stable")
        old_updated = note.updated_at
        # Update with same content
        note.update(content="Stable")
        assert note.updated_at == old_updated

    def test_update_content_only(self):
        """Should update only content if tags are None."""
        note = Note.create(content="Start", tags=["tag"])
        old_tags = note.tags.copy()
        note.update(content="Updated")
        assert note.content == "Updated"
        assert note.tags == old_tags

    def test_update_tags_only(self):
        """Should update only tags if content is None."""
        note = Note.create(content="Content", tags=["old"])
        note.update(tags=["new"])
        assert note.content == "Content"
        assert "new" in note.tags


class TestNoteTagOperations:
    """Tests for individual tag operations."""

    def test_add_tag_single(self):
        """Should add a single tag."""
        note = Note.create(content="Content", tags=["existing"])
        note.add_tag("new")
        assert "new" in note.tags
        assert "existing" in note.tags

    def test_add_tag_avoids_duplicates(self):
        """Should not add duplicate tags."""
        note = Note.create(content="Content", tags=["unique"])
        note.add_tag("unique")
        assert note.tags.count("unique") == 1

    def test_add_tag_updates_timestamp(self):
        """add_tag should update updated_at."""
        note = Note.create(content="Content")
        old_updated = note.updated_at
        note.add_tag("tag")
        assert note.updated_at != old_updated

    def test_remove_tag_single(self):
        """Should remove a tag."""
        note = Note.create(content="Content", tags=["first", "second"])
        note.remove_tag("first")
        assert "first" not in note.tags
        assert "second" in note.tags

    def test_remove_tag_nonexistent_is_noop(self):
        """Removing nonexistent tag should be safe."""
        note = Note.create(content="Content", tags=["existing"])
        note.remove_tag("missing")
        assert note.tags == ["existing"]

    def test_remove_tag_updates_timestamp(self):
        """remove_tag should update updated_at."""
        note = Note.create(content="Content", tags=["tag"])
        old_updated = note.updated_at
        note.remove_tag("tag")
        assert note.updated_at != old_updated

    def test_has_tag_existing(self):
        """Should return True for existing tag."""
        note = Note.create(content="Content", tags=["present"])
        assert note.has_tag("present")

    def test_has_tag_nonexistent(self):
        """Should return False for missing tag."""
        note = Note.create(content="Content", tags=["present"])
        assert not note.has_tag("missing")

    def test_has_tag_case_insensitive(self):
        """Tag check should be case-insensitive."""
        note = Note.create(content="Content", tags=["Present"])
        assert note.has_tag("present")
        assert note.has_tag("PRESENT")

    def test_has_tag_empty_string(self):
        """Empty tag should return False."""
        note = Note.create(content="Content", tags=["tag"])
        assert not note.has_tag("")

    def test_has_any_tag_with_matches(self):
        """Should return True if any tag matches."""
        note = Note.create(content="Content", tags=["one", "two"])
        assert note.has_any_tag(["one", "missing"])
        assert note.has_any_tag(["two", "other"])

    def test_has_any_tag_no_matches(self):
        """Should return False if no tags match."""
        note = Note.create(content="Content", tags=["one", "two"])
        assert not note.has_any_tag(["missing", "other"])

    def test_has_any_tag_empty_list(self):
        """Should return False for empty query list."""
        note = Note.create(content="Content", tags=["one"])
        assert not note.has_any_tag([])

    def test_has_all_tags_all_present(self):
        """Should return True if all tags present."""
        note = Note.create(content="Content", tags=["one", "two", "three"])
        assert note.has_all_tags(["one", "two"])
        assert note.has_all_tags(["one", "two", "three"])

    def test_has_all_tags_some_missing(self):
        """Should return False if any tag missing."""
        note = Note.create(content="Content", tags=["one", "two"])
        assert not note.has_all_tags(["one", "two", "three"])
        assert not note.has_all_tags(["one", "missing"])

    def test_has_all_tags_empty_list(self):
        """Should return True for empty query list (vacuous truth)."""
        note = Note.create(content="Content")
        assert note.has_all_tags([])


class TestNotePreview:
    """Tests for preview functionality."""

    def test_preview_short_content(self):
        """Short content should return full content."""
        note = Note.create(content="Short")
        assert note.get_preview(100) == "Short"

    def test_preview_exactly_max_length(self):
        """Content exactly at max length should not be truncated."""
        content = "x" * 50
        note = Note.create(content=content)
        assert note.get_preview(50) == content

    def test_preview_exceeds_max_length(self):
        """Content exceeding max length should be truncated."""
        content = "x" * 100
        note = Note.create(content=content)
        preview = note.get_preview(50)
        assert len(preview) <= 50
        assert preview.endswith("...")

    def test_preview_with_default_length(self):
        """Should use default length of 100."""
        content = "x" * 200
        note = Note.create(content=content)
        preview = note.get_preview()
        assert len(preview) <= 100

    def test_preview_preserves_content_start(self):
        """Preview should start with actual content."""
        content = "Important information at the start of a very long note"
        note = Note.create(content=content)
        preview = note.get_preview(20)
        assert preview.startswith("Important")

    def test_preview_very_small_max_length(self):
        """Should handle very small max_length values."""
        note = Note.create(content="Hello world")
        preview = note.get_preview(1)
        # Even with max_length=1, preview still includes min content + "..."
        assert len(preview) > 1
        assert "..." in preview

    def test_preview_empty_content(self):
        """Should handle minimal content (less than 2 chars fails validation)."""
        # Note content must be at least 2 chars (validator requirement)
        note = Note.create(content="ab")
        preview = note.get_preview()
        assert preview == "ab"

    def test_preview_multiline_content(self):
        """Newlines are normalized in content and preview."""
        content = "Line 1\nLine 2\nLine 3"
        note = Note.create(content=content)
        preview = note.get_preview(100)
        # Newlines are normalized to spaces
        expected = "Line 1 Line 2 Line 3"
        assert preview == expected
        assert "\n" not in preview


class TestNoteSearch:
    """Tests for search functionality."""

    def test_search_matches_content(self):
        """Should find note by content."""
        note = Note.create(content="Find this text")
        assert note.matches_search("find")
        assert note.matches_search("this")
        assert note.matches_search("text")

    def test_search_case_insensitive(self):
        """Search should be case-insensitive."""
        note = Note.create(content="Content Text")
        assert note.matches_search("CONTENT")
        assert note.matches_search("text")
        assert note.matches_search("CoNtEnT")

    def test_search_matches_tags(self):
        """Should find note by tags."""
        note = Note.create(content="Content", tags=["important", "urgent"])
        assert note.matches_search("important")
        assert note.matches_search("urgent")

    def test_search_partial_tag_match(self):
        """Should match partial tag strings."""
        note = Note.create(content="Content", tags=["important"])
        assert note.matches_search("import")
        assert note.matches_search("ant")

    def test_search_partial_content_match(self):
        """Should match partial content strings."""
        note = Note.create(content="The quick brown fox")
        assert note.matches_search("quick")
        assert note.matches_search("brow")

    def test_search_empty_query(self):
        """Empty search query matches all notes."""
        note = Note.create(content="Content")
        # Empty query matches everything
        assert note.matches_search("")
        # Whitespace-only query is not treated as match
        assert not note.matches_search("   ")
        assert not note.matches_search("   ")

    def test_search_no_match(self):
        """Non-matching query should return False."""
        note = Note.create(content="Content")
        assert not note.matches_search("xyz")
        assert not note.matches_search("nonexistent")

    def test_search_special_characters(self):
        """Should handle special characters in query."""
        note = Note.create(content="Price: $10.99")
        assert note.matches_search("$10")
        assert note.matches_search(".")


class TestNoteTimestamps:
    """Tests for timestamp behavior."""

    def test_timestamps_on_creation(self):
        """created_at and updated_at should be set on creation."""
        note = Note.create(content="Content")
        assert note.created_at
        assert note.updated_at

    def test_created_at_immutable(self):
        """created_at should not change on updates."""
        note = Note.create(content="Original")
        original_created = note.created_at
        note.update(content="Updated")
        assert note.created_at == original_created

    def test_updated_at_changes_on_content_update(self):
        """updated_at should change when content updates."""
        note = Note.create(content="Original")
        old_updated = note.updated_at
        note.update(content="Updated")
        assert note.updated_at != old_updated

    def test_updated_at_changes_on_tag_add(self):
        """updated_at should change when tag is added."""
        note = Note.create(content="Content")
        old_updated = note.updated_at
        note.add_tag("new")
        assert note.updated_at != old_updated

    def test_updated_at_changes_on_tag_remove(self):
        """updated_at should change when tag is removed."""
        note = Note.create(content="Content", tags=["tag"])
        old_updated = note.updated_at
        note.remove_tag("tag")
        assert note.updated_at != old_updated
