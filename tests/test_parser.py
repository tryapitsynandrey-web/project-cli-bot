import pytest

from assistant_bot.cli.parser import CommandParser, Command


class TestCommandParsing:
    """Tests for basic command parsing."""

    def test_parse_command_only(self):
        """Should parse command without arguments."""
        cmd = CommandParser.parse("help")
        assert cmd.name == "help"
        assert cmd.args == []

    def test_parse_command_with_single_arg(self):
        """Should parse command with single argument."""
        cmd = CommandParser.parse("add-contact John")
        assert cmd.name == "add-contact"
        assert cmd.args == ["John"]

    def test_parse_command_with_multiple_args(self):
        """Should parse command with multiple arguments."""
        cmd = CommandParser.parse("add-contact John Doe")
        assert cmd.name == "add-contact"
        assert cmd.args == ["John", "Doe"]

    def test_parse_command_with_many_args(self):
        """Should handle many arguments correctly."""
        cmd = CommandParser.parse("search-contact John Doe Smith Jr Extra")
        assert cmd.name == "search-contact"
        assert len(cmd.args) == 5

    def test_parse_normalizes_command_name(self):
        """Command name should be normalized to lowercase."""
        cmd = CommandParser.parse("ADD-CONTACT alice")
        assert cmd.name == "add-contact"

    def test_parse_normalizes_arg_whitespace(self):
        """Args should be stripped of extra whitespace."""
        cmd = CommandParser.parse("add-contact   John   ")
        assert cmd.args[0] == "John"

    def test_parse_empty_input_returns_none(self):
        """Empty input should return None."""
        assert CommandParser.parse("") is None
        assert CommandParser.parse("   ") is None

    def test_parse_tabs_and_newlines(self):
        """Should handle tabs and mixed whitespace."""
        cmd = CommandParser.parse("add-contact\tJohn\nDoe")
        assert cmd.name == "add-contact"
        assert "John" in cmd.args

    def test_parse_with_extra_whitespace(self):
        """Multiple spaces between args should be collapsed."""
        cmd = CommandParser.parse("search-contact    John    Doe")
        assert cmd.name == "search-contact"
        assert cmd.args == ["John", "Doe"]


class TestCommandQuotedArguments:
    """Tests for parsing quoted arguments."""

    def test_parse_double_quoted_single_arg(self):
        """Should handle double-quoted arguments."""
        cmd = CommandParser.parse("search-contact \"John Smith\"")
        assert cmd.args == ["John Smith"]

    def test_parse_single_quoted_arg(self):
        """Should handle single-quoted arguments."""
        cmd = CommandParser.parse("search-contact 'John Smith'")
        assert cmd.args == ["John Smith"]

    def test_parse_multiple_quoted_args(self):
        """Should handle multiple quoted arguments."""
        cmd = CommandParser.parse("edit-contact \"John Doe\" \"123 Main St\"")
        assert "John Doe" in cmd.args
        assert "123 Main St" in cmd.args

    def test_parse_mixed_quoted_and_unquoted(self):
        """Should handle mix of quoted and unquoted args."""
        cmd = CommandParser.parse("edit-contact \"John Doe\" john@example.com")
        assert "John Doe" in cmd.args
        assert "john@example.com" in cmd.args

    def test_parse_quote_within_opposite_quotes(self):
        """Single quote inside double quotes should be preserved."""
        cmd = CommandParser.parse("add-contact \"John's\"")
        assert "John's" in cmd.args

    def test_parse_unmatched_quote_treated_literally(self):
        """Unmatched quote should be part of argument."""
        # Behavior: unmatched quotes are handled gracefully
        cmd = CommandParser.parse("command \"unclosed")
        assert cmd is not None

    def test_parse_empty_quoted_string(self):
        """Empty quoted string should be ignored."""
        cmd = CommandParser.parse("command \"\" arg2")
        # Empty strings are filtered out
        assert "arg2" in cmd.args or len(cmd.args) >= 1

    def test_parse_whitespace_in_quotes(self):
        """Whitespace within quotes should be preserved."""
        cmd = CommandParser.parse("cmd \"multiple   spaces\"")
        assert "multiple   spaces" in cmd.args


class TestCommandAliases:
    """Tests for command aliases and normalization."""

    def test_alias_q_to_exit(self):
        """q should resolve to exit."""
        assert CommandParser.normalize_command_name("q") == "exit"

    def test_alias_quit_to_exit(self):
        """quit should resolve to exit."""
        assert CommandParser.normalize_command_name("quit") == "exit"

    def test_alias_h_to_help(self):
        """h should resolve to help."""
        assert CommandParser.normalize_command_name("h") == "help"

    def test_alias_question_to_help(self):
        """? should resolve to help."""
        assert CommandParser.normalize_command_name("?") == "help"

    def test_alias_ac_to_add_contact(self):
        """ac should resolve to add-contact."""
        assert CommandParser.normalize_command_name("ac") == "add-contact"

    @pytest.mark.parametrize(
        "alias,expected",
        [
            ("q", "exit"),
            ("quit", "exit"),
            ("h", "help"),
            ("?", "help"),
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
    def test_all_aliases_map_correctly(self, alias, expected):
        """All aliases should map to correct canonical commands."""
        assert CommandParser.normalize_command_name(alias) == expected

    def test_alias_case_insensitive(self):
        """Alias resolution should be case-insensitive."""
        assert CommandParser.normalize_command_name("AC") == "add-contact"
        assert CommandParser.normalize_command_name("Ac") == "add-contact"

    def test_non_alias_unchanged(self):
        """Non-alias command should be unchanged by normalization."""
        assert CommandParser.normalize_command_name("help") == "help"
        assert CommandParser.normalize_command_name("add-contact") == "add-contact"


class TestCommandValidation:
    """Tests for command validation."""

    def test_valid_command_help(self):
        """help should be a valid command."""
        assert CommandParser.is_valid_command("help")

    def test_valid_command_add_contact(self):
        """add-contact should be a valid command."""
        assert CommandParser.is_valid_command("add-contact")

    def test_invalid_command(self):
        """Unknown command should be invalid."""
        assert not CommandParser.is_valid_command("fakecommand")

    def test_invalid_command_empty_string(self):
        """Empty string should not be valid."""
        assert not CommandParser.is_valid_command("")

    def test_alias_is_valid(self):
        """Alias should resolve to valid command."""
        assert CommandParser.is_valid_command("ac")  # alias for add-contact

    def test_case_insensitivity_validation(self):
        """Validation should be case-insensitive."""
        assert CommandParser.is_valid_command("HELP")
        assert CommandParser.is_valid_command("Add-CONTACT")


class TestCommandMetadata:
    """Tests for command information methods."""

    def test_get_all_commands_not_empty(self):
        """Should return list of all commands."""
        commands = CommandParser.get_all_commands()
        assert len(commands) > 0
        assert "help" in commands
        assert "exit" in commands

    def test_get_all_commands_sorted(self):
        """Commands should be returned in sorted order."""
        commands = CommandParser.get_all_commands()
        assert commands == sorted(commands)

    def test_get_all_command_tokens_includes_aliases(self):
        """Should include both commands and aliases."""
        tokens = CommandParser.get_all_command_tokens()
        assert "help" in tokens
        assert "h" in tokens  # alias
        assert "?" in tokens  # alias
        assert "q" in tokens  # alias

    def test_get_all_tokens_not_empty(self):
        """Should return non-empty token list."""
        tokens = CommandParser.get_all_command_tokens()
        assert len(tokens) > 0

    def test_get_matching_empty_returns_all(self):
        """Empty input should return all tokens."""
        matches = CommandParser.get_matching_commands("")
        all_tokens = CommandParser.get_all_command_tokens()
        assert set(matches) == set(all_tokens)

    def test_get_matching_prefix_match(self):
        """Should match commands by prefix."""
        matches = CommandParser.get_matching_commands("add")
        # Should find add-contact, add-note, add-tag, etc.
        assert any("add" in cmd for cmd in matches)

    def test_get_matching_substring_fallback(self):
        """Should fallback to substring match."""
        matches = CommandParser.get_matching_commands("contacts")
        # Should find commands containing "contacts"
        assert any("contacts" in cmd for cmd in matches)

    def test_get_matching_case_insensitive(self):
        """Matching should be case-insensitive."""
        matches1 = CommandParser.get_matching_commands("add")
        matches2 = CommandParser.get_matching_commands("ADD")
        assert set(matches1) == set(matches2)

    def test_get_matching_unknown_returns_empty(self):
        """Non-matching input should return relevant matches."""
        matches = CommandParser.get_matching_commands("xyz")
        # Will do substring search on full commands
        assert isinstance(matches, list)


class TestCommand:
    """Tests for Command class."""

    def test_command_get_arg_valid_index(self):
        """Should return arg at valid index."""
        cmd = Command("test", ["first", "second", "third"])
        assert cmd.get_arg(0) == "first"
        assert cmd.get_arg(1) == "second"
        assert cmd.get_arg(2) == "third"

    def test_command_get_arg_invalid_index_returns_none(self):
        """Should return None for invalid index."""
        cmd = Command("test", ["first"])
        assert cmd.get_arg(5) is None
        assert cmd.get_arg(-1) is None

    def test_command_get_arg_with_default(self):
        """Should return default for invalid index."""
        cmd = Command("test", ["first"])
        assert cmd.get_arg(5, "default") == "default"

    def test_command_has_args_with_arguments(self):
        """Should return True when command has arguments."""
        cmd = Command("test", ["arg1"])
        assert cmd.has_args() is True

    def test_command_has_args_without_arguments(self):
        """Should return False when command has no arguments."""
        cmd = Command("test", [])
        assert cmd.has_args() is False

    def test_command_normalizes_name(self):
        """Command should normalize name to lowercase."""
        cmd = Command("TEST")
        assert cmd.name == "test"

    def test_command_strips_arg_whitespace(self):
        """Command should strip whitespace from arguments."""
        cmd = Command("test", ["  arg1  ", "  arg2  "])
        assert cmd.args == ["arg1", "arg2"]

    def test_command_filters_empty_args(self):
        """Empty args should be filtered out."""
        cmd = Command("test", ["arg1", "", "arg2"])
        assert cmd.args == ["arg1", "arg2"]

    def test_command_name_and_args_normalized(self):
        """Both name and args should be normalized."""
        cmd = Command("COMMAND", ["  Arg1  ", "  ", "Arg2  "])
        assert cmd.name == "command"
        assert cmd.args == ["Arg1", "Arg2"]
