"""Shared typing protocol for CLI handler mixins."""

from __future__ import annotations

from typing import Any, Protocol, TYPE_CHECKING

if TYPE_CHECKING:
    from assistant_bot.services.birthday_service import BirthdayService
    from assistant_bot.services.contact_service import ContactService
    from assistant_bot.services.note_service import NoteService
    from assistant_bot.services.suggestion_service import SuggestionService


class HandlerBase(Protocol):
    """Typing contract for command handler mixins."""

    contact_service: ContactService
    note_service: NoteService
    birthday_service: BirthdayService
    suggestion_service: SuggestionService

    @staticmethod
    def _parse_csv_values(raw_value: str) -> list[str]: ...

    @staticmethod
    def _print_hint(message: str) -> None: ...

    def _print_prompt_meta(
        self,
        *,
        example: str | None = None,
        rules: list[str] | None = None,
        optional: bool = False,
        allow_cancel: bool = False,
    ) -> None: ...

    @staticmethod
    def _print_section_intro(
        title: str,
        description: str | None = None,
    ) -> None: ...

    @staticmethod
    def _normalize_user_input(value: str) -> str: ...

    def _prompt_input(
        self,
        prompt: str,
        *,
        required: bool = False,
        allow_cancel: bool = False,
    ) -> str | None: ...

    def _prompt_required_value(
        self,
        prompt: str,
        *,
        example: str | None = None,
        rules: list[str] | None = None,
        allow_cancel: bool = False,
    ) -> str | None: ...

    def _prompt_optional_value(
        self,
        prompt: str,
        *,
        example: str | None = None,
        rules: list[str] | None = None,
        allow_cancel: bool = False,
    ) -> str | None: ...

    def _prompt_csv_values(
        self,
        prompt: str,
        *,
        required: bool = False,
        example: str | None = None,
        rules: list[str] | None = None,
        allow_cancel: bool = False,
    ) -> list[str] | None: ...

    def _prompt_contact_name(
        self,
        *,
        prompt: str = "Contact name: ",
        allow_cancel: bool = False,
    ) -> str | None: ...

    @staticmethod
    def _format_contact_choice(contact: Any) -> str: ...

    def _select_from_list(
        self,
        items: list[Any],
        *,
        item_label: str,
        formatter: Any,
    ) -> Any: ...

    def _select_from_contacts(self, contacts: list[Any]) -> Any: ...

    def _select_contact_by_name(self, contact_name: str) -> Any: ...

    def _confirm_action(self, prompt: str = "Confirm action [y/n]: ") -> bool: ...