"""ANSI color codes and rendering utilities."""

from __future__ import annotations

from datetime import datetime
from typing import Any, Iterable


class Color:
    """ANSI color codes for terminal output."""

    RESET = "\033[0m"
    BOLD = "\033[1m"
    DIM = "\033[2m"

    RED = "\033[91m"
    GREEN = "\033[92m"
    YELLOW = "\033[93m"
    BLUE = "\033[94m"
    MAGENTA = "\033[95m"
    CYAN = "\033[96m"
    WHITE = "\033[97m"


class Renderer:
    """Utilities for colored and formatted terminal output."""

    NONE_PLACEHOLDER = "(none)"
    DATETIME_OUTPUT_FORMAT = "%Y-%m-%d %H:%M"

    @staticmethod
    def success(message: str) -> str:
        """Format a success message."""
        return f"{Color.GREEN}✓ {message}{Color.RESET}"

    @staticmethod
    def error(message: str) -> str:
        """Format an error message."""
        return f"{Color.RED}✗ {message}{Color.RESET}"

    @staticmethod
    def warning(message: str) -> str:
        """Format a warning message."""
        return f"{Color.YELLOW}⚠ {message}{Color.RESET}"

    @staticmethod
    def info(message: str) -> str:
        """Format an informational message."""
        return f"{Color.BLUE}ℹ {message}{Color.RESET}"

    @staticmethod
    def header(text: str) -> str:
        """Format a section header."""
        return f"\n{Color.BOLD}{Color.CYAN}{text}{Color.RESET}"

    @staticmethod
    def highlight(text: str) -> str:
        """Highlight text."""
        return f"{Color.BOLD}{Color.CYAN}{text}{Color.RESET}"

    @staticmethod
    def bold(text: str) -> str:
        """Make text bold."""
        return f"{Color.BOLD}{text}{Color.RESET}"

    @staticmethod
    def dim(text: str) -> str:
        """Dim text."""
        return f"{Color.DIM}{text}{Color.RESET}"

    @staticmethod
    def _display(value: Any) -> str:
        """Return a printable representation for optional values."""
        if value is None:
            return Renderer.NONE_PLACEHOLDER
        if isinstance(value, str) and not value.strip():
            return Renderer.NONE_PLACEHOLDER
        return str(value)

    @staticmethod
    def _format_datetime(value: str | None) -> str:
        """Format ISO datetime safely for display."""
        if not value:
            return Renderer.NONE_PLACEHOLDER

        try:
            parsed = datetime.fromisoformat(value)
        except (TypeError, ValueError):
            return Renderer.NONE_PLACEHOLDER

        return parsed.strftime(Renderer.DATETIME_OUTPUT_FORMAT)

    @staticmethod
    def _join_values(values: Iterable[str] | None, separator: str = ", ") -> str:
        """Join printable values or return a placeholder."""
        if not values:
            return Renderer.NONE_PLACEHOLDER

        cleaned = [str(value).strip() for value in values if str(value).strip()]
        if not cleaned:
            return Renderer.NONE_PLACEHOLDER

        return separator.join(cleaned)

    @staticmethod
    def _format_tags(tags: Iterable[str] | None, separator: str = ", ") -> str:
        """Format tags with a leading # symbol."""
        if not tags:
            return Renderer.NONE_PLACEHOLDER

        cleaned = [f"#{tag.strip()}" for tag in tags if str(tag).strip()]
        if not cleaned:
            return Renderer.NONE_PLACEHOLDER

        return separator.join(cleaned)

    @staticmethod
    def render_contact(contact: Any) -> str:
        """Render a contact in a readable card format."""
        from assistant_bot.utils.datetime_utils import format_birthday

        id_short = str(contact.contact_id)[:8]
        name = Renderer._display(getattr(contact, "name", None))
        phones = Renderer._join_values(getattr(contact, "phone_numbers", []))
        email = Renderer._display(getattr(contact, "email", None))
        address = Renderer._display(getattr(contact, "address", None))
        birthday = Renderer._display(format_birthday(getattr(contact, "birthday", None)))
        note = Renderer._display(getattr(contact, "note", None))
        tags = Renderer._format_tags(getattr(contact, "tags", []))

        lines = [
            f"┌─ {Renderer.highlight(name)} [{id_short}]",
            f"├─ Email:    {email}",
            f"├─ Phone:    {phones}",
            f"├─ Address:  {address}",
            f"├─ Birthday: {birthday}",
            f"├─ Note:     {note}",
            f"└─ Tags:     {tags}",
        ]
        return "\n".join(lines)

    @staticmethod
    def render_contact_short(contact: Any) -> str:
        """Render a contact in compact form."""
        name = Renderer._display(getattr(contact, "name", None))
        phones = Renderer._join_values(getattr(contact, "phone_numbers", []))
        email = Renderer._display(getattr(contact, "email", None))
        return f"{Renderer.highlight(name)} - {email} - {phones}"

    @staticmethod
    def render_note(note: Any) -> str:
        """Render a note in a readable card format."""
        note_id = str(getattr(note, "note_id", ""))[:8]
        content = Renderer._display(getattr(note, "content", None))
        created = Renderer._format_datetime(getattr(note, "created_at", None))
        updated = Renderer._format_datetime(getattr(note, "updated_at", None))
        tags = Renderer._format_tags(getattr(note, "tags", []), separator=" ")

        lines = [
            f"┌─ Note [{note_id}]",
            f"├─ Content: {Renderer.highlight(content)}",
            f"├─ Created: {created}",
            f"├─ Updated: {updated}",
            f"└─ Tags:    {Renderer.dim(tags) if tags != Renderer.NONE_PLACEHOLDER else tags}",
        ]
        return "\n".join(lines)

    @staticmethod
    def render_note_short(note: Any) -> str:
        """Render a note in compact form."""
        preview = note.get_preview(60)
        tags = Renderer._format_tags(getattr(note, "tags", []), separator=" ")
        if tags != Renderer.NONE_PLACEHOLDER:
            return f"{preview} {Renderer.dim(tags)}"
        return preview

    @staticmethod
    def table_header(columns: list[str], widths: list[int]) -> str:
        """Render a simple table header."""
        parts = [column.ljust(width) for column, width in zip(columns, widths)]
        header = " | ".join(parts)
        separator = "-" * len(header)
        return f"{Renderer.bold(header)}\n{separator}"

    @staticmethod
    def render_command_suggestions(commands: list[str]) -> str:
        """Render matching command suggestions."""
        if not commands:
            return ""
        formatted = "   ".join(commands)
        return Renderer.dim(formatted)