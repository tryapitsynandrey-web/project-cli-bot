"""CLI command handlers package."""

from __future__ import annotations

from assistant_bot.cli.handlers.contact_commands import ContactCommandsMixin
from assistant_bot.cli.handlers.contact_tag_commands import ContactTagCommandsMixin
from assistant_bot.cli.handlers.internal_helper_methods import (
    InternalHelperMethodsMixin,
)
from assistant_bot.cli.handlers.note_commands import NoteCommandsMixin
from assistant_bot.cli.handlers.system_commands import SystemCommandsMixin
from assistant_bot.services.birthday_service import BirthdayService
from assistant_bot.services.contact_service import ContactService
from assistant_bot.services.note_service import NoteService
from assistant_bot.services.suggestion_service import SuggestionService


class CommandHandler(
    InternalHelperMethodsMixin,
    ContactCommandsMixin,
    ContactTagCommandsMixin,
    NoteCommandsMixin,
    SystemCommandsMixin,
):
    """Handle CLI commands."""

    def __init__(
        self,
        contact_service: ContactService,
        note_service: NoteService,
        birthday_service: BirthdayService,
        suggestion_service: SuggestionService,
    ) -> None:
        """Initialize command handler services."""
        super().__init__()
        self.contact_service = contact_service
        self.note_service = note_service
        self.birthday_service = birthday_service
        self.suggestion_service = suggestion_service


__all__ = ["CommandHandler"]