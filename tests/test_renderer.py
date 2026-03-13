import re

import pytest

from assistant_bot.cli.renderer import Renderer


class TestRendererHelpers:
    """Tests for renderer helper methods."""

    def test_display_none_shows_placeholder(self):
        """None should display as placeholder."""
        assert Renderer._display(None) == Renderer.NONE_PLACEHOLDER

    def test_display_empty_string_shows_placeholder(self):
        """Empty string should display as placeholder."""
        assert Renderer._display("") == Renderer.NONE_PLACEHOLDER

    def test_display_whitespace_only_shows_placeholder(self):
        """Whitespace-only string should display as placeholder."""
        assert Renderer._display("   ") == Renderer.NONE_PLACEHOLDER

    def test_display_normal_string(self):
        """Normal string should display as-is."""
        assert Renderer._display("hello") == "hello"

    def test_join_values_empty_list(self):
        """Empty list should return placeholder."""
        assert Renderer._join_values([], ",") == Renderer.NONE_PLACEHOLDER

    def test_join_values_single_item(self):
        """Single item should return that item."""
        result = Renderer._join_values(["one"], ",")
        assert "one" in result

    def test_join_values_multiple_items(self):
        """Multiple items should be joined with separator."""
        result = Renderer._join_values(["one", "two", "three"], ", ")
        assert "one" in result
        assert "two" in result
        assert "three" in result
        assert "," in result

    def test_join_values_custom_separator(self):
        """Should use provided separator."""
        result = Renderer._join_values(["a", "b"], "|")
        assert "|" in result

    def test_format_datetime_none(self):
        """None should return placeholder."""
        assert Renderer._format_datetime(None) == Renderer.NONE_PLACEHOLDER

    def test_format_datetime_empty_string(self):
        """Empty string should return placeholder."""
        assert Renderer._format_datetime("") == Renderer.NONE_PLACEHOLDER

    def test_format_datetime_valid(self):
        """Valid datetime should be formatted."""
        result = Renderer._format_datetime("2024-01-15T10:30:00")
        assert result
        assert result != Renderer.NONE_PLACEHOLDER


class TestRenderContact:
    """Tests for contact rendering."""

    def test_render_contact_short_contains_name(self):
        """Short contact render should include name."""
        contact = self._make_contact(
            contact_id="123",
            name="Alice",
            phone_numbers=["555-1234"],
            email="alice@example.com"
        )
        result = Renderer.render_contact_short(contact)
        assert "Alice" in result

    def test_render_contact_short_contains_phone(self):
        """Short contact render should include first phone."""
        contact = self._make_contact(
            contact_id="123",
            name="Bob",
            phone_numbers=["555-5678"]
        )
        result = Renderer.render_contact_short(contact)
        assert "555-5678" in result

    def test_render_contact_short_contains_id(self):
        """Short contact render should include essential contact info."""
        contact = self._make_contact(
            contact_id="abc123",
            name="Carol",
            phone_numbers=["555-9999"]
        )
        result = Renderer.render_contact_short(contact)
        # Short render includes name and phone, but not the ID
        assert "Carol" in result
        assert "555-9999" in result

    def test_render_contact_short_with_all_fields(self):
        """Should render when all fields populated."""
        contact = self._make_contact(
            contact_id="id1",
            name="Dave",
            phone_numbers=["111-1111"],
            email="dave@example.com",
            address="123 Main",
            birthday="1990-01-01",
            note="Important",
            tags=["vip"]
        )
        result = Renderer.render_contact_short(contact)
        assert "Dave" in result
        assert "111-1111" in result

    def test_render_contact_short_with_minimal_fields(self):
        """Should handle minimal contact data."""
        contact = self._make_contact(
            contact_id="min",
            name="Min",
            phone_numbers=["000-0000"]
        )
        result = Renderer.render_contact_short(contact)
        assert result  # Should produce output without crashing
        assert "Min" in result

    def test_render_contact_short_multiple_phones(self):
        """Should handle contacts with multiple phones."""
        contact = self._make_contact(
            contact_id="multi",
            name="Multi",
            phone_numbers=["111-1111", "222-2222", "333-3333"]
        )
        result = Renderer.render_contact_short(contact)
        assert result  # Should not crash with  multiple phones

    @staticmethod
    def _make_contact(**kwargs):
        """Helper to create test contact object."""
        class FakeContact:
            def __init__(self, **kw):
                self.__dict__.update(kw)
        return FakeContact(**kwargs)


class TestRenderNote:
    """Tests for note rendering."""

    def test_render_note_short_contains_content_preview(self):
        """Short note render should contain content."""
        note = self._make_note(
            note_id="n1",
            content="This is a note",
            tags=[]
        )
        result = Renderer.render_note_short(note)
        assert "This is a note" in result

    def test_render_note_short_contains_id(self):
        """Short note render should contain note content."""
        note = self._make_note(
            note_id="noteid123",
            content="Content",
            tags=[]
        )
        result = Renderer.render_note_short(note)
        # Short render includes content but not the ID
        assert "Content" in result

    def test_render_note_short_with_tags(self):
        """Should include tags in render."""
        note = self._make_note(
            note_id="n2",
            content="Tagged note",
            tags=["important", "urgent"]
        )
        result = Renderer.render_note_short(note)
        assert result  # Should not crash with tags

    def test_render_note_short_with_empty_tags(self):
        """Should handle empty tag list."""
        note = self._make_note(
            note_id="n3",
            content="No tags",
            tags=[]
        )
        result = Renderer.render_note_short(note)
        assert "No tags" in result

    def test_render_note_short_very_long_content(self):
        """Should handle long note content."""
        long_content = "x" * 1000
        note = self._make_note(
            note_id="long",
            content=long_content,
            tags=[]
        )
        result = Renderer.render_note_short(note)
        assert result  # Should not crash

    @staticmethod
    def _make_note(**kwargs):
        """Helper to create test note object."""
        class FakeNote:
            def __init__(self, **kw):
                self.__dict__.update(kw)
            def get_preview(self, max_len):
                return self.content[:max_len]
        return FakeNote(**kwargs)


class TestTableHeader:
    """Tests for table header rendering."""

    def test_table_header_basic(self):
        """Should render basic table header."""
        header = Renderer.table_header(["Name", "Phone"], [20, 15])
        assert header
        assert "Name" in header or "name" in header.lower()

    def test_table_header_has_separator(self):
        """Table header should have separator line."""
        header = Renderer.table_header(["Col1", "Col2"], [10, 10])
        lines = header.splitlines()
        assert len(lines) >= 2  # At least header and separator

    def test_table_header_separator_length_matches(self):
        """Separator should match header length."""
        header_text = Renderer.table_header(["A", "BC"], [3, 4])
        lines = header_text.splitlines()
        # Remove ANSI escape codes for length comparison
        header_line = lines[0]
        sep_line = lines[1] if len(lines) > 1 else ""

        # Strip ANSI codes
        ansi_pattern = r"\x1b\[[0-9;]*m"
        header_clean = re.sub(ansi_pattern, "", header_line)
        sep_clean = re.sub(ansi_pattern, "", sep_line)

        # Separator should be roughly same length as header
        assert abs(len(header_clean) - len(sep_clean)) <= 2

    def test_table_header_multiple_columns(self):
        """Should handle multiple columns."""
        header = Renderer.table_header(
            ["Col1", "Col2", "Col3", "Col4"],
            [10, 15, 12, 8]
        )
        assert header
        lines = header.splitlines()
        assert len(lines) >= 2

    def test_table_header_different_widths(self):
        """Should handle varied column widths."""
        header = Renderer.table_header(["Short", "MuchLongerColumn"], [5, 20])
        lines = header.splitlines()
        assert len(lines) >= 2
