import pytest

from assistant_bot.cli.help_text import (
    get_help_text,
    MAIN_HELP,
    COMMAND_HELP,
    ALIASES,
    MENU_SECTIONS,
    MENU_WIDTH,
    _render_menu_line,
    _render_section,
)


class TestMainHelp:
    """Tests for main menu help text."""

    def test_main_help_not_empty(self):
        """Main help text should not be empty."""
        assert MAIN_HELP
        assert len(MAIN_HELP) > 100

    def test_main_help_contains_sections(self):
        """Main help should display all menu sections."""
        for section_name in MENU_SECTIONS.keys():
            assert section_name in MAIN_HELP

    def test_main_help_border_formatting(self):
        """Main help should have proper box-drawing characters."""
        assert "╔" in MAIN_HELP  # top-left
        assert "╗" in MAIN_HELP  # top-right
        assert "╠" in MAIN_HELP  # divider
        assert "║" in MAIN_HELP  # sides
        assert "╚" in MAIN_HELP  # bottom-left
        assert "╝" in MAIN_HELP  # bottom-right

    def test_get_help_text_none_returns_main(self):
        """Calling get_help_text() with None returns main help."""
        assert get_help_text(None) == MAIN_HELP

    def test_get_help_text_no_args_returns_main(self):
        """Calling get_help_text() with no args returns main help."""
        assert get_help_text() == MAIN_HELP


class TestCommandHelp:
    """Tests for specific command help text."""

    @pytest.mark.parametrize(
        "command",
        [
            "help",
            "exit",
            "add-contact",
            "list-contacts",
            "search-contact",
            "edit-contact",
            "delete-contact",
            "birthdays",
            "add-note",
            "list-notes",
            "search-notes",
            "edit-note",
            "delete-note",
            "notes-by-tag",
            "add-tag",
            "edit-tag",
            "delete-tag",
            "list-tags",
            "contacts-by-tag",
        ],
    )
    def test_all_main_commands_have_help(self, command):
        """All main commands should have help text."""
        help_text = get_help_text(command)
        assert help_text, f"No help for command: {command}"
        assert "Unknown command" not in help_text

    @pytest.mark.parametrize(
        "alias,canonical",
        [
            ("h", "help"),
            ("?", "help"),
            ("q", "exit"),
            ("quit", "exit"),
            ("ac", "add-contact"),
            ("ls", "list-contacts"),
            ("sc", "search-contact"),
            ("ec", "edit-contact"),
            ("dc", "delete-contact"),
            ("bd", "birthdays"),
            ("an", "add-note"),
            ("ln", "list-notes"),
            ("sn", "search-notes"),
            ("en", "edit-note"),
            ("dn", "delete-note"),
            ("at", "add-tag"),
            ("et", "edit-tag"),
            ("dt", "delete-tag"),
            ("lt", "list-tags"),
            ("ct", "contacts-by-tag"),
            ("nbt", "notes-by-tag"),
        ],
    )
    def test_alias_resolves_to_canonical(self, alias, canonical):
        """Aliases should resolve to canonical command help."""
        alias_help = get_help_text(alias)
        canonical_help = get_help_text(canonical)
        assert alias_help == canonical_help
        assert "Unknown command" not in alias_help

    def test_get_specific_command_help(self):
        """Should return correct help for specific commands."""
        contact_help = get_help_text("add-contact")
        assert "Add a new contact" in contact_help
        assert "Name" in contact_help or "phone" in contact_help.lower()

        note_help = get_help_text("add-note")
        assert "Add a new note" in note_help
        assert "content" in note_help.lower() or "Note content" in note_help

    def test_help_command_help(self):
        """Help command should describe its own usage."""
        help_text = get_help_text("help")
        assert "help" in help_text.lower()
        assert "Usage" in help_text or "usage" in help_text.lower()

    def test_exit_command_has_aliases_listed(self):
        """Exit help should mention its aliases."""
        exit_help = get_help_text("exit")
        assert "quit" in exit_help.lower() or "q" in exit_help
        assert "Alias" in exit_help or "alias" in exit_help.lower()


class TestUnknownCommands:
    """Tests for handling unknown/invalid commands."""

    @pytest.mark.parametrize(
        "unknown_cmd",
        ["nope", "fake", "invalid-command", "xyz", "help-me", ""],
    )
    def test_unknown_command_shows_error(self, unknown_cmd):
        """Unknown commands should show error message."""
        help_text = get_help_text(unknown_cmd)
        assert "Unknown command" in help_text
        assert unknown_cmd in help_text

    def test_case_sensitivity_of_commands(self):
        """Commands are case-sensitive (specific behavior verification)."""
        # get_help_text does not normalize case, so uppercase shouldn't match
        upper_help = get_help_text("ADD-CONTACT")
        assert "Unknown command" in upper_help


class TestAliasConsistency:
    """Tests for ALIASES dictionary consistency."""

    def test_all_aliases_map_to_valid_commands(self):
        """Every alias should map to a command with help text."""
        for alias, canonical in ALIASES.items():
            canonical_help = COMMAND_HELP.get(canonical)
            assert canonical_help is not None, (
                f"Alias '{alias}' maps to '{canonical}' "
                f"which has no help text"
            )

    def test_alias_dictionary_not_empty(self):
        """ALIASES dictionary should contain mappings."""
        assert len(ALIASES) > 0


class TestMenuStructure:
    """Tests for menu section structure."""

    def test_menu_sections_not_empty(self):
        """MENU_SECTIONS should contain section data."""
        assert len(MENU_SECTIONS) > 0

    def test_all_section_items_tuples(self):
        """Each section should contain command/description tuples."""
        for section_name, items in MENU_SECTIONS.items():
            assert isinstance(items, list), (
                f"Section '{section_name}' items should be a list"
            )
            for item in items:
                assert isinstance(item, tuple), (
                    f"Section '{section_name}' should contain tuples"
                )
                assert len(item) == 2, (
                    f"Section '{section_name}' tuples should be (command, desc)"
                )
                command, description = item
                assert isinstance(command, str) and command
                assert isinstance(description, str) and description


class TestRenderingHelpers:
    """Tests for render helper functions."""

    def test_render_menu_line_format(self):
        """Menu line should have consistent format."""
        line = _render_menu_line("test-cmd", "Test description")
        assert "║" in line
        assert "test-cmd" in line
        assert "Test description" in line

    def test_render_menu_line_width(self):
        """Menu line should respect MENU_WIDTH."""
        line = _render_menu_line("cmd", "desc")
        # Should be roughly MENU_WIDTH + sidebars
        assert len(line) >= MENU_WIDTH

    def test_render_section_contains_title(self):
        """Rendered section should include section title."""
        lines = _render_section("TEST", [("cmd", "desc")])
        rendered = "\n".join(lines)
        assert "TEST" in rendered

    def test_render_section_contains_items(self):
        """Rendered section should contain all items."""
        items = [("cmd1", "desc1"), ("cmd2", "desc2")]
        lines = _render_section("TEST", items)
        rendered = "\n".join(lines)
        assert "cmd1" in rendered
        assert "cmd2" in rendered
        assert "desc1" in rendered
        assert "desc2" in rendered

    def test_render_section_empty_items(self):
        """Should handle empty item list gracefully."""
        lines = _render_section("EMPTY", [])
        assert len(lines) > 0
        rendered = "\n".join(lines)
        assert "EMPTY" in rendered
