"""Main application orchestrator."""

from __future__ import annotations

from collections.abc import Callable
from typing import Any

from assistant_bot.cli.handlers import CommandHandler
from assistant_bot.cli.parser import Command, CommandParser
from assistant_bot.cli.renderer import Renderer
from assistant_bot.services.birthday_service import BirthdayService
from assistant_bot.services.contact_service import ContactService
from assistant_bot.services.note_service import NoteService
from assistant_bot.services.suggestion_service import SuggestionService
from assistant_bot.storage.json_storage import JSONStorage

try:
    from prompt_toolkit import PromptSession
    from prompt_toolkit.completion import WordCompleter

    PROMPT_TOOLKIT_AVAILABLE = True
except ImportError:
    PromptSession = None
    WordCompleter = None
    PROMPT_TOOLKIT_AVAILABLE = False


class PersonalAssistant:
    """Main CLI application."""

    def __init__(self) -> None:
        """Initialize application services and command infrastructure."""
        self.storage = JSONStorage()

        self.contact_service = ContactService(self.storage)
        self.note_service = NoteService(self.storage)
        self.birthday_service = BirthdayService(self.contact_service)
        self.suggestion_service = SuggestionService()

        self.handler = CommandHandler(
            self.contact_service,
            self.note_service,
            self.birthday_service,
            self.suggestion_service,
        )

        self.running = False
        self.session: Any = self._create_prompt_session()
        self.command_dispatch = self._build_command_dispatch()

    def _create_prompt_session(self) -> Any:
        """Create an interactive prompt session with command completion support."""
        if not PROMPT_TOOLKIT_AVAILABLE or PromptSession is None or WordCompleter is None:
            return None

        commands = CommandParser.get_all_command_tokens()
        completer = WordCompleter(
            commands,
            ignore_case=True,
            sentence=True,
        )
        return PromptSession(completer=completer)

    def _build_command_dispatch(self) -> dict[str, Callable[[Command], bool]]:
        """Build the command dispatch table."""
        return {
            "help": self._dispatch_help,
            "exit": self._dispatch_exit,
            "add-contact": lambda command: self._run_handler(
                self.handler.handle_add_contact,
                command,
            ),
            "list-contacts": lambda command: self._run_handler(
                self.handler.handle_list_contacts,
                command,
            ),
            "search-contact": lambda command: self._run_handler_with_arg(
                self.handler.handle_search_contact,
                command,
            ),
            "edit-contact": lambda command: self._run_handler_with_arg(
                self.handler.handle_edit_contact,
                command,
            ),
            "delete-contact": lambda command: self._run_handler_with_arg(
                self.handler.handle_delete_contact,
                command,
            ),
            "birthdays": lambda command: self._run_handler_with_arg(
                self.handler.handle_birthdays,
                command,
            ),
            "add-tag": lambda command: self._run_handler(
                self.handler.handle_add_tag,
                command,
            ),
            "edit-tag": lambda command: self._run_handler(
                self.handler.handle_edit_tag,
                command,
            ),
            "delete-tag": lambda command: self._run_handler(
                self.handler.handle_delete_tag,
                command,
            ),
            "list-tags": lambda command: self._run_handler(
                self.handler.handle_list_tags,
                command,
            ),
            "contacts-by-tag": lambda command: self._run_handler_with_arg(
                self.handler.handle_view_contacts_by_tag,
                command,
            ),
            "add-note": lambda command: self._run_handler(
                self.handler.handle_add_note,
                command,
            ),
            "list-notes": lambda command: self._run_handler(
                self.handler.handle_list_notes,
                command,
            ),
            "search-notes": lambda command: self._run_handler_with_arg(
                self.handler.handle_search_notes,
                command,
            ),
            "edit-note": lambda command: self._run_handler_with_arg(
                self.handler.handle_edit_note,
                command,
            ),
            "delete-note": lambda command: self._run_handler_with_arg(
                self.handler.handle_delete_note,
                command,
            ),
            "notes-by-tag": self._dispatch_notes_by_tag,
        }

    def _run_handler(self, handler: Callable[[], None], command: Command) -> bool:
        """Run a handler that requires no parsed arguments."""
        _ = command
        handler()
        return True

    def _run_handler_with_arg(
        self,
        handler: Callable[[str | None], None],
        command: Command,
    ) -> bool:
        """Run a handler that accepts the first parsed argument."""
        handler(command.get_arg(0))
        return True

    def _dispatch_help(self, command: Command) -> bool:
        """Dispatch the help command."""
        self.handler.handle_help(command.get_arg(0))
        return True

    def _dispatch_exit(self, command: Command) -> bool:
        """Dispatch exit command."""
        _ = command
        return False

    def _dispatch_notes_by_tag(self, command: Command) -> bool:
        """Dispatch notes-by-tag with reconstructed argument string."""
        self.handler.handle_notes_by_tag(" ".join(command.args))
        return True

    def show_welcome(self) -> None:
        """Show the welcome block and command menu."""
        print("\n" + "=" * 60)
        print(Renderer.highlight("Welcome to Personal Assistant"))
        print("=" * 60)
        self.handler.handle_help()

        if PROMPT_TOOLKIT_AVAILABLE:
            print(Renderer.info("Command suggestions are available while typing."))
        else:
            print(Renderer.warning("Interactive command suggestions are unavailable."))

    def process_command(self, command_text: str) -> bool:
        """Parse and dispatch a single command string."""
        command = CommandParser.parse(command_text)
        if command is None:
            return True

        dispatch = self.command_dispatch.get(command.name)
        if dispatch is None:
            self.handler.handle_unknown_command(command.name)
            return True

        return dispatch(command)

    def _prompt_text(self) -> str:
        """Return the styled input prompt."""
        return f"\n{Renderer.highlight('> ')}"

    def _read_user_input(self) -> str:
        """Read user input using the best available input method."""
        prompt_text = self._prompt_text()

        if self.session is not None:
            return self.session.prompt(prompt_text)

        return input(prompt_text)

    def run(self) -> None:
        """Run the main application loop."""
        self.running = True
        self.show_welcome()

        try:
            while self.running:
                try:
                    user_input = self._read_user_input()

                    if not user_input or not user_input.strip():
                        continue

                    should_continue = self.process_command(user_input)
                    if not should_continue:
                        self.running = False

                except KeyboardInterrupt:
                    print(f"\n{Renderer.info('Use exit or quit to exit.')}")
                except EOFError:
                    print()
                    self.running = False
                except Exception as error:
                    print(Renderer.error(f"Unexpected error: {error}"))

        finally:
            print(f"\n{Renderer.success('Goodbye!')}")