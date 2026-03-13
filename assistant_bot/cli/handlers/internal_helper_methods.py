"""Internal helper methods for CLI command handlers."""

from __future__ import annotations

from typing import Any

from assistant_bot.cli.handlers.base import HandlerBase
from assistant_bot.cli.interaction import CLIInteraction
from assistant_bot.cli.renderer import Renderer


class InternalHelperMethodsMixin(HandlerBase):
    """Shared internal helper methods for CLI command handlers."""

    def __init__(self) -> None:
        """Initialize shared CLI interaction helpers."""
        self.ui = CLIInteraction()

    @staticmethod
    def _parse_csv_values(raw_value: str) -> list[str]:
        """Split comma-separated input into a normalized list of values."""
        return CLIInteraction.parse_csv_values(raw_value)

    @staticmethod
    def _print_hint(message: str) -> None:
        """Print a dimmed helper hint."""
        CLIInteraction.print_hint(message)

    def _print_prompt_meta(
        self,
        *,
        example: str | None = None,
        rules: list[str] | None = None,
        optional: bool = False,
        allow_cancel: bool = False,
    ) -> None:
        """Print standardized helper text before prompting the user."""
        self.ui.print_prompt_meta(
            example=example,
            rules=rules,
            optional=optional,
            allow_cancel=allow_cancel,
        )

    @staticmethod
    def _print_section_intro(title: str, description: str | None = None) -> None:
        """Print a section header with an optional short description."""
        CLIInteraction.print_section_intro(title, description)

    @staticmethod
    def _normalize_user_input(value: str) -> str:
        """Normalize raw user input."""
        return CLIInteraction.normalize_user_input(value)

    def _prompt_input(
        self,
        prompt: str,
        *,
        required: bool = False,
        allow_cancel: bool = False,
    ) -> str | None:
        """Prompt the user for input with optional required and cancel behavior."""
        return self.ui.prompt_input(
            prompt,
            required=required,
            allow_cancel=allow_cancel,
        )

    def _prompt_required_value(
        self,
        prompt: str,
        *,
        example: str | None = None,
        rules: list[str] | None = None,
        allow_cancel: bool = False,
    ) -> str | None:
        """Prompt for a required value."""
        return self.ui.prompt_required_value(
            prompt,
            example=example,
            rules=rules,
            allow_cancel=allow_cancel,
        )

    def _prompt_optional_value(
        self,
        prompt: str,
        *,
        example: str | None = None,
        rules: list[str] | None = None,
        allow_cancel: bool = False,
    ) -> str | None:
        """Prompt for an optional value."""
        return self.ui.prompt_optional_value(
            prompt,
            example=example,
            rules=rules,
            allow_cancel=allow_cancel,
        )

    def _prompt_csv_values(
        self,
        prompt: str,
        *,
        required: bool = False,
        example: str | None = None,
        rules: list[str] | None = None,
        allow_cancel: bool = False,
    ) -> list[str] | None:
        """Prompt for comma-separated values and return them as a normalized list."""
        return self.ui.prompt_csv_values(
            prompt,
            required=required,
            example=example,
            rules=rules,
            allow_cancel=allow_cancel,
        )

    def _prompt_contact_name(
        self,
        *,
        prompt: str = "Contact name: ",
        allow_cancel: bool = False,
    ) -> str | None:
        """Prompt for a contact name."""
        return self.ui.prompt_contact_name(
            prompt=prompt,
            allow_cancel=allow_cancel,
        )

    @staticmethod
    def _format_contact_choice(contact: Any) -> str:
        """Format one contact row for interactive selection."""
        return CLIInteraction.format_contact_choice(contact)

    def _select_from_list(
        self,
        items: list[Any],
        *,
        item_label: str,
        formatter,
    ):
        """Let the user select one item from a list."""
        return self.ui.select_from_list(
            items,
            item_label=item_label,
            formatter=formatter,
        )

    def _select_from_contacts(self, contacts: list[Any]):
        """Let the user select one contact from a list."""
        return self.ui.select_from_contacts(contacts)

    def _select_contact_by_name(self, contact_name: str):
        """Find a contact by name and resolve duplicates via interactive selection."""
        contacts = self.contact_service.get_contacts_by_name(contact_name)

        if not contacts:
            print(Renderer.error(f"No contacts found with name '{contact_name}'."))
            return None

        return self._select_from_contacts(contacts)

    def _confirm_action(self, prompt: str = "Confirm action [y/n]: ") -> bool:
        """Ask the user to confirm an action."""
        return self.ui.confirm_action(prompt)