"""Interactive CLI input/output helpers."""

from __future__ import annotations

from collections.abc import Callable
from typing import Any

from assistant_bot.cli.renderer import Renderer


class CLIInteraction:
    """Interactive CLI helper for prompts, hints, selections, and confirmations."""

    @staticmethod
    def parse_csv_values(raw_value: str) -> list[str]:
        """Split comma-separated input into a normalized list of values."""
        return [item.strip() for item in raw_value.split(",") if item.strip()]

    @staticmethod
    def print_hint(message: str) -> None:
        """Print a dimmed helper hint."""
        print(Renderer.dim(message))

    def print_prompt_meta(
        self,
        *,
        example: str | None = None,
        rules: list[str] | None = None,
        optional: bool = False,
        allow_cancel: bool = False,
    ) -> None:
        """Print standardized helper text before prompting the user."""
        if rules:
            for rule in rules:
                self.print_hint(rule)

        if example:
            self.print_hint(f"Example: {example}")

        if optional:
            self.print_hint("Press Enter to skip this field.")

        if allow_cancel:
            self.print_hint("Type 'cancel' to cancel this action.")

    @staticmethod
    def print_section_intro(title: str, description: str | None = None) -> None:
        """Print a section header with an optional short description."""
        print(Renderer.header(title))
        if description:
            print(Renderer.dim(description))

    @staticmethod
    def normalize_user_input(value: str) -> str:
        """Normalize raw user input."""
        return value.strip()

    def prompt_input(
        self,
        prompt: str,
        *,
        required: bool = False,
        allow_cancel: bool = False,
    ) -> str | None:
        """Prompt the user for input with optional required and cancel behavior."""
        while True:
            value = self.normalize_user_input(input(prompt))

            if allow_cancel and value.lower() == "cancel":
                return None

            if required and not value:
                print(Renderer.error("This field is required."))
                continue

            return value

    def prompt_required_value(
        self,
        prompt: str,
        *,
        example: str | None = None,
        rules: list[str] | None = None,
        allow_cancel: bool = False,
    ) -> str | None:
        """Prompt for a required value."""
        self.print_prompt_meta(
            example=example,
            rules=rules,
            optional=False,
            allow_cancel=allow_cancel,
        )
        return self.prompt_input(
            prompt,
            required=True,
            allow_cancel=allow_cancel,
        )

    def prompt_optional_value(
        self,
        prompt: str,
        *,
        example: str | None = None,
        rules: list[str] | None = None,
        allow_cancel: bool = False,
    ) -> str | None:
        """Prompt for an optional value."""
        self.print_prompt_meta(
            example=example,
            rules=rules,
            optional=True,
            allow_cancel=allow_cancel,
        )
        return self.prompt_input(
            prompt,
            required=False,
            allow_cancel=allow_cancel,
        )

    def prompt_csv_values(
        self,
        prompt: str,
        *,
        required: bool = False,
        example: str | None = None,
        rules: list[str] | None = None,
        allow_cancel: bool = False,
    ) -> list[str] | None:
        """Prompt for comma-separated values and return them as a normalized list."""
        self.print_prompt_meta(
            example=example,
            rules=rules,
            optional=not required,
            allow_cancel=allow_cancel,
        )

        while True:
            raw_value = self.prompt_input(
                prompt,
                required=required,
                allow_cancel=allow_cancel,
            )

            if raw_value is None:
                return None

            values = self.parse_csv_values(raw_value)

            if required and not values:
                print(Renderer.error("Please provide at least one value."))
                continue

            return values

    def prompt_contact_name(
        self,
        *,
        prompt: str = "Contact name: ",
        allow_cancel: bool = False,
    ) -> str | None:
        """Prompt for a contact name."""
        return self.prompt_required_value(
            prompt,
            example="John Smith",
            allow_cancel=allow_cancel,
        )

    @staticmethod
    def format_contact_choice(contact: Any) -> str:
        """Format one contact row for interactive selection."""
        phones = ", ".join(contact.phone_numbers) if contact.phone_numbers else "(none)"
        email = contact.email if contact.email else "(no email)"
        return f"{contact.name} | {phones} | {email}"

    def select_from_list(
        self,
        items: list[Any],
        *,
        item_label: str,
        formatter: Callable[[Any], str],
    ) -> Any | None:
        """Let the user select one item from a list."""
        if not items:
            return None

        if len(items) == 1:
            return items[0]

        print(f"\nFound {len(items)} {item_label}:")
        for index, item in enumerate(items, start=1):
            print(f"{index}. {formatter(item)}")

        while True:
            choice = self.prompt_input(
                f"Select {item_label.rstrip('s')} number (or type 'cancel'): ",
                allow_cancel=True,
            )

            if choice is None:
                print("Cancelled.")
                return None

            try:
                selected_index = int(choice) - 1
                return items[selected_index]
            except (ValueError, IndexError):
                print(Renderer.error("Invalid selection. Please enter a valid number."))

    def select_from_contacts(self, contacts: list[Any]) -> Any | None:
        """Let the user select one contact from a list."""
        return self.select_from_list(
            contacts,
            item_label="contacts",
            formatter=self.format_contact_choice,
        )

    def confirm_action(self, prompt: str = "Confirm action [y/n]: ") -> bool:
        """Ask the user to confirm an action."""
        while True:
            answer = self.normalize_user_input(input(prompt)).lower()

            if answer in {"y", "yes"}:
                return True
            if answer in {"n", "no"}:
                return False

            print(Renderer.error("Please enter 'y'/'yes' or 'n'/'no'."))