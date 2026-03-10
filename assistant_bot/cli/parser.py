"""Command parsing and command metadata utilities."""

from dataclasses import dataclass, field


@dataclass(slots=True)
class Command:
    """Represent a parsed CLI command."""

    name: str
    args: list[str] = field(default_factory=list)

    def __post_init__(self) -> None:
        """Normalize command name and arguments after initialization."""
        self.name = self.name.lower().strip()
        self.args = [arg.strip() for arg in self.args if arg.strip()]

    def get_arg(self, index: int, default: str | None = None) -> str | None:
        """Return an argument by index or the provided default value."""
        if 0 <= index < len(self.args):
            return self.args[index]
        return default

    def has_args(self) -> bool:
        """Return True if the command contains arguments."""
        return bool(self.args)


class CommandParser:
    """Parse raw CLI input into structured commands."""

    VALID_COMMANDS = {
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
    }

    ALIASES = {
        "q": "exit",
        "quit": "exit",
        "h": "help",
        "?": "help",
        "ac": "add-contact",
        "ls": "list-contacts",
        "sc": "search-contact",
        "ec": "edit-contact",
        "dc": "delete-contact",
        "bd": "birthdays",
        "an": "add-note",
        "ln": "list-notes",
        "sn": "search-notes",
        "en": "edit-note",
        "dn": "delete-note",
        "at": "add-tag",
        "et": "edit-tag",
        "dt": "delete-tag",
        "lt": "list-tags",
        "ct": "contacts-by-tag",
        "nbt": "notes-by-tag",
    }

    @classmethod
    def parse(cls, user_input: str) -> Command | None:
        """Parse raw user input into a Command object."""
        normalized_input = user_input.strip()
        if not normalized_input:
            return None

        parts = normalized_input.split(maxsplit=1)
        command_name = cls.normalize_command_name(parts[0])
        args_str = parts[1] if len(parts) > 1 else ""

        args = cls._parse_args(args_str)
        return Command(command_name, args)

    @classmethod
    def normalize_command_name(cls, command_name: str) -> str:
        """Resolve aliases and normalize a command name."""
        normalized = command_name.lower().strip()
        return cls.ALIASES.get(normalized, normalized)

    @classmethod
    def _parse_args(cls, args_str: str) -> list[str]:
        """Parse an argument string into a list of arguments."""
        if not args_str.strip():
            return []

        args: list[str] = []
        current: list[str] = []
        quote_char: str | None = None

        for char in args_str:
            if char in {'"', "'"}:
                if quote_char is None:
                    quote_char = char
                elif quote_char == char:
                    quote_char = None
                else:
                    current.append(char)
            elif char.isspace() and quote_char is None:
                if current:
                    args.append("".join(current).strip())
                    current = []
            else:
                current.append(char)

        if current:
            args.append("".join(current).strip())

        return [arg for arg in args if arg]

    @classmethod
    def is_valid_command(cls, command_name: str) -> bool:
        """Return True if the command name is valid."""
        return cls.normalize_command_name(command_name) in cls.VALID_COMMANDS

    @classmethod
    def get_all_commands(cls) -> list[str]:
        """Return all canonical command names sorted alphabetically."""
        return sorted(cls.VALID_COMMANDS)

    @classmethod
    def get_all_command_tokens(cls) -> list[str]:
        """Return all commands and aliases for interactive suggestions."""
        return sorted(set(cls.VALID_COMMANDS) | set(cls.ALIASES.keys()))

    @classmethod
    def get_matching_commands(cls, partial_input: str) -> list[str]:
        """Return commands and aliases that match the current partial input."""
        normalized = partial_input.lower().strip()
        if not normalized:
            return cls.get_all_command_tokens()

        prefix_matches = [
            token
            for token in cls.get_all_command_tokens()
            if token.startswith(normalized)
        ]
        if prefix_matches:
            return prefix_matches

        return [
            command
            for command in cls.get_all_commands()
            if normalized in command
        ]