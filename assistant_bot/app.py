"""Main application orchestrator."""

from __future__ import annotations

from collections.abc import Callable
from typing import Any

from assistant_bot.cli.command_registry import CommandRegistry
from assistant_bot.cli.handlers import CommandHandler
from assistant_bot.cli.parser import Command, CommandParser
from assistant_bot.cli.renderer import Renderer
from assistant_bot.cli.results import CommandResult
from assistant_bot.repositories import JSONContactRepository, JSONNoteRepository
from assistant_bot.services.birthday_service import BirthdayService
from assistant_bot.services.contact_service import ContactService
from assistant_bot.services.note_service import NoteService
from assistant_bot.services.suggestion_service import SuggestionService
from assistant_bot.storage.json_storage import JSONStorage

try:
    from prompt_toolkit import PromptSession
    from prompt_toolkit.completion import WordCompleter
    from prompt_toolkit.formatted_text import ANSI

    PROMPT_TOOLKIT_AVAILABLE = True
except ImportError:
    PromptSession = None
    WordCompleter = None
    ANSI = None
    PROMPT_TOOLKIT_AVAILABLE = False


class PersonalAssistant:
    """Main CLI application."""

    def __init__(self) -> None:
        """Initialize application services and command infrastructure."""
        self.storage = JSONStorage()

        self.contact_repository = JSONContactRepository(self.storage)
        self.note_repository = JSONNoteRepository(self.storage)

        self.contact_service = ContactService(self.contact_repository)
        self.note_service = NoteService(self.note_repository)
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
        self.command_registry = self._build_command_registry()

    def _create_prompt_session(self) -> Any:
        """Create an interactive prompt session with command completion support."""
        if (
            not PROMPT_TOOLKIT_AVAILABLE
            or PromptSession is None
            or WordCompleter is None
        ):
            return None

        commands = CommandParser.get_all_command_tokens()
        completer = WordCompleter(
            commands,
            ignore_case=True,
            sentence=True,
        )
        return PromptSession(completer=completer)

    def _build_command_registry(self) -> CommandRegistry:
        """Build and populate the command registry."""
        registry = CommandRegistry()

        registry.register("help", self._dispatch_help)
        registry.register("exit", self._dispatch_exit)

        registry.register(
            "add-contact",
            lambda command: self._run_result_handler(
                self.handler.handle_add_contact,
                command,
            ),
        )
        registry.register(
            "list-contacts",
            lambda command: self._run_result_handler(
                self.handler.handle_list_contacts,
                command,
            ),
        )
        registry.register(
            "search-contact",
            lambda command: self._run_result_handler_with_arg(
                self.handler.handle_search_contact,
                command,
            ),
        )
        registry.register(
            "edit-contact",
            lambda command: self._run_result_handler_with_arg(
                self.handler.handle_edit_contact,
                command,
            ),
        )
        registry.register(
            "delete-contact",
            lambda command: self._run_result_handler_with_arg(
                self.handler.handle_delete_contact,
                command,
            ),
        )
        registry.register(
            "birthdays",
            lambda command: self._run_result_handler_with_arg(
                self.handler.handle_birthdays,
                command,
            ),
        )

        registry.register(
            "add-tag",
            lambda command: self._run_result_handler(
                self.handler.handle_add_tag,
                command,
            ),
        )
        registry.register(
            "edit-tag",
            lambda command: self._run_result_handler(
                self.handler.handle_edit_tag,
                command,
            ),
        )
        registry.register(
            "delete-tag",
            lambda command: self._run_result_handler(
                self.handler.handle_delete_tag,
                command,
            ),
        )
        registry.register(
            "list-tags",
            lambda command: self._run_result_handler(
                self.handler.handle_list_tags,
                command,
            ),
        )
        registry.register(
            "contacts-by-tag",
            lambda command: self._run_result_handler_with_arg(
                self.handler.handle_view_contacts_by_tag,
                command,
            ),
        )

        registry.register(
            "add-note",
            lambda command: self._run_result_handler(
                self.handler.handle_add_note,
                command,
            ),
        )
        registry.register(
            "list-notes",
            lambda command: self._run_result_handler(
                self.handler.handle_list_notes,
                command,
            ),
        )
        registry.register(
            "search-notes",
            lambda command: self._run_result_handler_with_arg(
                self.handler.handle_search_notes,
                command,
            ),
        )
        registry.register(
            "edit-note",
            lambda command: self._run_result_handler_with_arg(
                self.handler.handle_edit_note,
                command,
            ),
        )
        registry.register(
            "delete-note",
            lambda command: self._run_result_handler_with_arg(
                self.handler.handle_delete_note,
                command,
            ),
        )
        registry.register("notes-by-tag", self._dispatch_notes_by_tag)

        return registry

    def _run_result_handler(
        self,
        handler: Callable[[], CommandResult],
        command: Command,
    ) -> bool:
        """Run a handler that returns a structured command result."""
        _ = command
        result = handler()
        self._render_command_result(result)
        return True

    def _run_result_handler_with_arg(
        self,
        handler: Callable[[str | None], CommandResult],
        command: Command,
    ) -> bool:
        """Run a handler with one argument that returns a structured command result."""
        result = handler(command.get_arg(0))
        self._render_command_result(result)
        return True

    def _dispatch_help(self, command: Command) -> bool:
        """Dispatch the help command."""
        result = self.handler.handle_help(command.get_arg(0))
        self._render_command_result(result)
        return True

    def _dispatch_exit(self, command: Command) -> bool:
        """Dispatch exit command."""
        _ = command
        return False

    def _dispatch_notes_by_tag(self, command: Command) -> bool:
        """Dispatch notes-by-tag with reconstructed argument string."""
        result = self.handler.handle_notes_by_tag(" ".join(command.args))
        self._render_command_result(result)
        return True

    def _render_command_result(self, result: CommandResult | None) -> None:
        """Render a structured command result to the CLI."""
        if result is None:
            return

        if result.status == "success":
            if result.message:
                print(Renderer.success(result.message))
        elif result.status == "error":
            if result.message:
                print(Renderer.error(result.message))
        elif result.status == "warning":
            if result.message:
                print(Renderer.warning(result.message))
        else:
            if result.message:
                print(Renderer.header(result.message))

        for detail in result.details:
            print(detail)

        self._render_command_result_data(result)

    def _render_notes(self, notes: list) -> None:
        """Render a list of notes."""
        for note in notes:
            print(Renderer.render_note(note))
            print()

    def _render_contacts(self, contacts: list) -> None:
        """Render a list of contacts."""
        for contact in contacts:
            print(Renderer.render_contact(contact))
            print()

    def _render_tag_counts(self, tags: list[tuple[str, int]]) -> None:
        """Render a list of tags with usage counts."""
        for tag, count in tags:
            print(f"#{tag} ({count} contact(s))")

    def _render_text_lines(self, lines: list[str]) -> None:
        """Render a list of plain text lines."""
        for line in lines:
            print(line)

    def _render_command_result_data(self, result: CommandResult) -> None:
        """Render structured data carried by a command result."""
        if result.data is None:
            return

        if isinstance(result.data, list) and result.data:
            first_item = result.data[0]

            if hasattr(first_item, "note_id"):
                self._render_notes(result.data)
                return

            if hasattr(first_item, "contact_id"):
                self._render_contacts(result.data)
                return

            if isinstance(first_item, str):
                self._render_text_lines(result.data)
                return

            if (
                isinstance(first_item, tuple)
                and len(first_item) == 2
                and isinstance(first_item[0], str)
                and isinstance(first_item[1], int)
            ):
                self._render_tag_counts(result.data)

    def show_welcome(self) -> None:
        """Show the welcome block and command menu."""
        print(Renderer.header("Welcome to Personal Assistant"))
        print(self.handler.handle_help().message or "")

        print()
        if PROMPT_TOOLKIT_AVAILABLE:
            print(Renderer.info("Command suggestions are available while typing."))
        else:
            print(Renderer.warning("Interactive command suggestions are unavailable."))

    def process_command(self, command_text: str) -> bool:
        """Parse and dispatch a single command string."""
        command = CommandParser.parse(command_text)
        if command is None:
            return True

        dispatch = self.command_registry.get(command.name)
        if dispatch is None:
            result = self.handler.handle_unknown_command(command.name)
            self._render_command_result(result)
            return True

        return dispatch(command)

    def _prompt_text(self) -> str:
        """Return the styled input prompt."""
        return Renderer.highlight("> ")

    def _read_user_input(self) -> str:
        """Read user input using the best available input method."""
        prompt_text = self._prompt_text()

        if self.session is not None and ANSI is not None:
            return self.session.prompt(ANSI(prompt_text))

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