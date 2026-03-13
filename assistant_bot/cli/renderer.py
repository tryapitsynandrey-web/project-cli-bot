"""ANSI color codes and rendering utilities."""

from __future__ import annotations

import re
import textwrap
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

    BOX_WIDTH = 66
    LABEL_WIDTH = 10
    CARD_SIDE_PADDING = 1
    CARD_GAP_BETWEEN_LABEL_AND_VALUE = 1

    ANSI_PATTERN = re.compile(r"\x1b\[[0-9;]*m")

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
        line = "═" * Renderer.BOX_WIDTH
        title = Renderer.bold(text)
        return (
            f"\n{Color.CYAN}{line}{Color.RESET}\n"
            f"{Color.CYAN}  {title}{Color.RESET}\n"
            f"{Color.CYAN}{line}{Color.RESET}"
        )

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
    def _strip_ansi(text: str) -> str:
        """Remove ANSI escape codes from a string."""
        return Renderer.ANSI_PATTERN.sub("", text)

    @staticmethod
    def _visible_len(text: str) -> int:
        """Return the visible length of a possibly colored string."""
        return len(Renderer._strip_ansi(text))

    @staticmethod
    def _truncate(text: str, max_width: int) -> str:
        """Truncate text to fit into a fixed visible width."""
        if max_width <= 0:
            return ""

        raw = Renderer._strip_ansi(text)
        if len(raw) <= max_width:
            return text

        if max_width == 1:
            return "…"

        return raw[: max_width - 1].rstrip() + "…"

    @staticmethod
    def _pad_visible(text: str, width: int) -> str:
        """Pad a string to a fixed visible width, preserving ANSI colors."""
        truncated = Renderer._truncate(text, width)
        padding = max(0, width - Renderer._visible_len(truncated))
        return f"{truncated}{' ' * padding}"

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
    def _wrap_text(text: str, width: int) -> list[str]:
        """Wrap plain text into lines of a maximum width."""
        clean = Renderer._display(text)
        if clean == Renderer.NONE_PLACEHOLDER:
            return [clean]

        wrapped = textwrap.wrap(
            clean,
            width=width,
            break_long_words=True,
            break_on_hyphens=False,
        )
        return wrapped or [Renderer.NONE_PLACEHOLDER]

    @staticmethod
    def _card_lines(title: str, rows: list[tuple[str, str]]) -> str:
        """Render a boxed card with a title and key-value rows."""
        inner_width = Renderer.BOX_WIDTH - 2
        value_width = (
            inner_width
            - Renderer.CARD_SIDE_PADDING
            - Renderer.LABEL_WIDTH
            - Renderer.CARD_GAP_BETWEEN_LABEL_AND_VALUE
            - Renderer.CARD_SIDE_PADDING
        )

        title_width = inner_width - (Renderer.CARD_SIDE_PADDING * 2)

        lines = [
            f"┌{'─' * inner_width}┐",
            f"│{' ' * Renderer.CARD_SIDE_PADDING}"
            f"{Renderer._pad_visible(title, title_width)}"
            f"{' ' * Renderer.CARD_SIDE_PADDING}│",
            f"├{'─' * inner_width}┤",
        ]

        for label, value in rows:
            wrapped_values = Renderer._wrap_text(value, value_width)
            padded_label = Renderer._pad_visible(
                f"{label}:",
                Renderer.LABEL_WIDTH,
            )

            first_value = Renderer._pad_visible(wrapped_values[0], value_width)
            lines.append(
                f"│{' ' * Renderer.CARD_SIDE_PADDING}"
                f"{padded_label}"
                f"{' ' * Renderer.CARD_GAP_BETWEEN_LABEL_AND_VALUE}"
                f"{first_value}"
                f"{' ' * Renderer.CARD_SIDE_PADDING}│"
            )

            for continuation in wrapped_values[1:]:
                empty_label = " " * Renderer.LABEL_WIDTH
                padded_value = Renderer._pad_visible(continuation, value_width)
                lines.append(
                    f"│{' ' * Renderer.CARD_SIDE_PADDING}"
                    f"{empty_label}"
                    f"{' ' * Renderer.CARD_GAP_BETWEEN_LABEL_AND_VALUE}"
                    f"{padded_value}"
                    f"{' ' * Renderer.CARD_SIDE_PADDING}│"
                )

        lines.append(f"└{'─' * inner_width}┘")
        return "\n".join(lines)

    @staticmethod
    def render_contact(contact: Any) -> str:
        """Render a contact in a readable card format."""
        from assistant_bot.utils.datetime_utils import format_birthday

        id_short = str(contact.contact_id)[:8]
        name = Renderer._display(getattr(contact, "name", None))
        phones = Renderer._join_values(getattr(contact, "phone_numbers", []))
        email = Renderer._display(getattr(contact, "email", None))
        address = Renderer._display(getattr(contact, "address", None))
        birthday = Renderer._display(
            format_birthday(getattr(contact, "birthday", None))
        )
        note = Renderer._display(getattr(contact, "note", None))
        tags = Renderer._format_tags(getattr(contact, "tags", []))

        title = f"{Renderer.highlight(name)} [{id_short}]"
        rows = [
            ("Email", email),
            ("Phone", phones),
            ("Address", address),
            ("Birthday", birthday),
            ("Note", note),
            ("Tags", tags),
        ]
        return Renderer._card_lines(title, rows)

    @staticmethod
    def render_contact_short(contact: Any) -> str:
        """Render a contact in compact form."""
        name = Renderer._display(getattr(contact, "name", None))
        phones = Renderer._join_values(getattr(contact, "phone_numbers", []))
        email = Renderer._display(getattr(contact, "email", None))
        return f"{Renderer.highlight(name)} · {email} · {phones}"

    @staticmethod
    def render_note(note: Any) -> str:
        """Render a note in a readable card format."""
        note_id = str(getattr(note, "note_id", ""))[:8]
        content = Renderer._display(getattr(note, "content", None))
        created = Renderer._format_datetime(getattr(note, "created_at", None))
        updated = Renderer._format_datetime(getattr(note, "updated_at", None))
        tags = Renderer._format_tags(getattr(note, "tags", []), separator=" ")

        title = Renderer.highlight(f"Note [{note_id}]")
        rows = [
            ("Content", Renderer.highlight(content)),
            ("Created", created),
            ("Updated", updated),
            (
                "Tags",
                Renderer.dim(tags)
                if tags != Renderer.NONE_PLACEHOLDER
                else tags,
            ),
        ]
        return Renderer._card_lines(title, rows)

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
        parts = [
            Renderer._pad_visible(column, width)
            for column, width in zip(columns, widths)
        ]
        header = " | ".join(parts)
        separator = "-" * Renderer._visible_len(header)
        return f"{Renderer.bold(header)}\n{separator}"

    @staticmethod
    def render_command_suggestions(commands: list[str]) -> str:
        """Render matching command suggestions."""
        if not commands:
            return ""
        formatted = "   ".join(commands)
        return Renderer.dim(formatted)