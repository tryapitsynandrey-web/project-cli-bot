"""CLI help text definitions and rendering utilities."""

from __future__ import annotations

MENU_WIDTH = 64
INNER_PADDING = 2
COLUMN_GAP = 3

MENU_TITLE = "Personal Assistant - Command Menu"
MAIN_HELP_FOOTER = [
    "Type 'help <command>' for command details.",
    "Tip: Use aliases in parentheses for faster typing.",
]

MENU_SECTIONS: dict[str, list[tuple[str, str]]] = {
    "CONTACTS": [
        ("add-contact (ac)", "Add a new contact"),
        ("list-contacts (ls)", "List all contacts"),
        ("search-contact (sc)", "Search contacts"),
        ("edit-contact (ec)", "Edit a contact"),
        ("delete-contact (dc)", "Delete a contact"),
        ("birthdays (bd)", "Show upcoming birthdays"),
    ],
    "NOTES": [
        ("add-note (an)", "Add a new note"),
        ("list-notes (ln)", "List all notes"),
        ("search-notes (sn)", "Search notes"),
        ("edit-note (en)", "Edit a note"),
        ("delete-note (dn)", "Delete a note"),
        ("notes-by-tag (nbt)", "Find notes by tag"),
    ],
    "TAGS": [
        ("add-tag (at)", "Add tag to a contact"),
        ("edit-tag (et)", "Edit a contact tag"),
        ("delete-tag (dt)", "Delete tag from a contact"),
        ("list-tags (lt)", "Show all contact tags"),
        ("contacts-by-tag (ct)", "Find contacts by tag"),
    ],
    "SYSTEM": [
        ("help [cmd]", "Show menu or command help"),
        ("exit | quit (q)", "Exit the application"),
    ],
}

COMMAND_HELP: dict[str, str] = {
    "help": """Show command help.

Usage:
  help
  help <command>

Examples:
  help
  help add-contact""",
    "h": "Alias for: help",
    "?": "Alias for: help",
    "exit": """Exit the application.

Aliases:
  quit
  q""",
    "quit": "Alias for: exit",
    "q": "Alias for: exit",
    "add-contact": """Add a new contact.

Usage:
  add-contact

Required fields:
  - Name
  - At least one phone number

Optional fields:
  - Email
  - Address
  - Birthday
  - Note
  - Tags""",
    "ac": "Alias for: add-contact",
    "list-contacts": """List all contacts.

Usage:
  list-contacts

Output:
  - Contacts sorted by name
  - Full formatted contact cards""",
    "ls": "Alias for: list-contacts",
    "search-contact": """Search contacts by partial match.

Usage:
  search-contact <query>

Search fields:
  - Name
  - Phone
  - Email
  - Address
  - Note
  - Tags

Examples:
  search-contact john
  search-contact +353
  search-contact work""",
    "sc": "Alias for: search-contact",
    "edit-contact": """Edit an existing contact.

Usage:
  edit-contact <contact-name>

Behavior:
  - If multiple contacts match, you will be asked to choose one
  - Editable fields include name, address, phones, email, birthday, note, and tags""",
    "ec": "Alias for: edit-contact",
    "delete-contact": """Delete a contact.

Usage:
  delete-contact <contact-name>

Behavior:
  - If multiple contacts match, you will be asked to choose one
  - Confirmation is required before deletion""",
    "dc": "Alias for: delete-contact",
    "birthdays": """Show upcoming birthdays.

Usage:
  birthdays [days]

Default:
  7 days

Examples:
  birthdays
  birthdays 30""",
    "bd": "Alias for: birthdays",
    "add-note": """Add a new note.

Usage:
  add-note

Required fields:
  - Note content

Optional fields:
  - Tags""",
    "an": "Alias for: add-note",
    "list-notes": """List all notes.

Usage:
  list-notes

Output:
  - Notes in the configured display order
  - Includes preview and tags when available""",
    "ln": "Alias for: list-notes",
    "search-notes": """Search notes by content.

Usage:
  search-notes <query>

Examples:
  search-notes meeting
  search-notes invoice""",
    "sn": "Alias for: search-notes",
    "edit-note": """Edit a note.

Usage:
  edit-note <note-id>

Editable fields:
  - Content
  - Tags""",
    "en": "Alias for: edit-note",
    "delete-note": """Delete a note.

Usage:
  delete-note <note-id>

Behavior:
  - Confirmation is required before deletion""",
    "dn": "Alias for: delete-note",
    "notes-by-tag": """Find notes by tag.

Usage:
  notes-by-tag [--any|--all] <tag1> [tag2] ...

Options:
  --any   Match notes with any listed tag
  --all   Match notes with all listed tags

Examples:
  notes-by-tag work
  notes-by-tag --all urgent finance""",
    "nbt": "Alias for: notes-by-tag",
    "add-tag": """Add one or more tags to a contact.

Usage:
  add-tag

Behavior:
  - You will be prompted for contact name
  - You will be prompted for comma-separated tags""",
    "at": "Alias for: add-tag",
    "edit-tag": """Edit a contact tag.

Usage:
  edit-tag

Behavior:
  - You will be prompted for contact name
  - You will be prompted for old tag and new tag""",
    "et": "Alias for: edit-tag",
    "delete-tag": """Delete one or more tags from a contact.

Usage:
  delete-tag

Behavior:
  - You will be prompted for contact name
  - You will be prompted for tags to delete""",
    "dt": "Alias for: delete-tag",
    "list-tags": """List all tags currently used by contacts.

Usage:
  list-tags

Output:
  - Tag name
  - Number of contacts using the tag""",
    "lt": "Alias for: list-tags",
    "contacts-by-tag": """Find all contacts with a given tag.

Usage:
  contacts-by-tag <tag>

Example:
  contacts-by-tag work""",
    "ct": "Alias for: contacts-by-tag",
}

ALIASES: dict[str, str] = {
    "h": "help",
    "?": "help",
    "q": "exit",
    "quit": "exit",
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


def _truncate(text: str, width: int) -> str:
    """Truncate text to the target width."""
    if width <= 0:
        return ""
    if len(text) <= width:
        return text
    if width == 1:
        return "…"
    return text[: width - 1].rstrip() + "…"


def _horizontal(char: str) -> str:
    """Build a horizontal line segment for the menu width."""
    return char * MENU_WIDTH


def _blank_line() -> str:
    """Render an empty menu line."""
    return f"║{'':{MENU_WIDTH}}║"


def _menu_columns() -> tuple[int, int]:
    """Return computed widths for command and description columns."""
    available = MENU_WIDTH - (INNER_PADDING * 2) - COLUMN_GAP
    longest_command = max(
        len(command)
        for items in MENU_SECTIONS.values()
        for command, _ in items
    )

    command_width = min(longest_command, max(18, available // 2))
    description_width = max(10, available - command_width)

    return command_width, description_width


def _render_menu_line(
    command: str,
    description: str,
    command_width: int | None = None,
    description_width: int | None = None,
) -> str:
    """Render one formatted menu row."""
    if command_width is None or description_width is None:
        command_width, description_width = _menu_columns()

    command_text = _truncate(command, command_width)
    description_text = _truncate(description, description_width)

    content = (
        f"{' ' * INNER_PADDING}"
        f"{command_text:<{command_width}}"
        f"{' ' * COLUMN_GAP}"
        f"{description_text:<{description_width}}"
        f"{' ' * INNER_PADDING}"
    )
    return f"║{content}║"


def _render_section(
    title: str,
    items: list[tuple[str, str]],
    command_width: int | None = None,
    description_width: int | None = None,
) -> list[str]:
    """Render one menu section."""
    if command_width is None or description_width is None:
        command_width, description_width = _menu_columns()

    title_line = (
        f"║{' ' * INNER_PADDING}"
        f"{title}:"
        f"{'':<{MENU_WIDTH - INNER_PADDING - len(title) - 1}}║"
    )

    lines = [title_line]
    lines.extend(
        _render_menu_line(
            command,
            description,
            command_width,
            description_width,
        )
        for command, description in items
    )
    lines.append(_blank_line())
    return lines


def build_main_help() -> str:
    """Build the main command menu."""
    command_width, description_width = _menu_columns()

    lines = [
        f"╔{_horizontal('═')}╗",
        f"║{MENU_TITLE:^{MENU_WIDTH}}║",
        f"╠{_horizontal('═')}╣",
        _blank_line(),
    ]

    for section_name, section_items in MENU_SECTIONS.items():
        lines.extend(
            _render_section(
                section_name,
                section_items,
                command_width,
                description_width,
            )
        )

    lines.append(f"╚{_horizontal('═')}╝")
    lines.append("")
    lines.extend(MAIN_HELP_FOOTER)

    return "\n".join(lines)


MAIN_HELP = build_main_help()


def get_help_text(command: str | None = None) -> str:
    """Return help text for the full menu or a specific command."""
    if command is None:
        return MAIN_HELP

    normalized = ALIASES.get(command, command)
    return COMMAND_HELP.get(normalized, f"Unknown command: {command}")