"""Note-related CLI command handlers."""

from __future__ import annotations

from assistant_bot.cli.handlers.base import HandlerBase
from assistant_bot.cli.renderer import Renderer
from assistant_bot.cli.results import CommandResult
from assistant_bot.domain.exceptions import NoteNotFoundError, ValidationError


class NoteCommandsMixin(HandlerBase):
    """Note-related CLI command handlers."""

    def handle_add_note(self) -> CommandResult:
        """Handle add-note command."""
        self._print_section_intro(
            "Add New Note",
            "Required field: note content.",
        )

        try:
            content = self._prompt_required_value(
                "Note content (required): ",
                example="Call the supplier on Friday about the invoice.",
                rules=[
                    "Write the main note text in one line.",
                ],
                allow_cancel=True,
            )
            if content is None:
                return CommandResult.info("Cancelled.")

            tags = self._prompt_csv_values(
                "Tags (optional): ",
                required=False,
                example="work, urgent, finance",
                rules=[
                    "Separate multiple tags with commas.",
                    "Tags are normalized automatically.",
                ],
                allow_cancel=True,
            )
            if tags is None:
                return CommandResult.info("Cancelled.")

            note = self.note_service.add_note(content, tags or [])

            return CommandResult.success(
                "Note added.",
                data=[note],
                details=[f"ID: {note.note_id}"],
            )

        except ValidationError as error:
            return CommandResult.error(f"Validation error: {error}")
        except ValueError as error:
            return CommandResult.error(f"Invalid input: {error}")

    def handle_list_notes(self) -> CommandResult:
        """Handle list-notes command."""
        notes = self.note_service.get_all_notes()

        if not notes:
            return CommandResult.info("No notes found.")

        return CommandResult.info(
            "All Notes",
            data=notes,
            details=[f"Total notes: {len(notes)}"],
        )

    def handle_search_notes(self, query: str | None) -> CommandResult:
        """Handle search-notes command."""
        if not query:
            return CommandResult.error(
                "Please provide a search query.",
                details=["Usage: search-notes <query>"],
            )

        results = self.note_service.search_notes(query)

        if not results:
            return CommandResult.info("No notes found matching your search.")

        return CommandResult.info(
            f"Search Results for '{query}'",
            data=results,
            details=[
                "Search is performed across note content.",
                f"Found {len(results)} note(s):",
            ],
        )

    def _edit_note_menu_lines(self, note) -> list[str]:
        """Build the interactive edit menu for a note."""
        tags = ", ".join(note.tags) if note.tags else "(none)"
        return [
            "What would you like to edit?",
            f"1. Content  ({note.get_preview(50)})",
            f"2. Tags     ({tags})",
            "0. Cancel",
        ]

    def _prompt_edit_note_choice(self, note) -> str | None:
        """Prompt the user for which note field to edit."""
        for line in self._edit_note_menu_lines(note):
            print(line)

        return self._prompt_input(
            "\nChoice (0-2): ",
            required=True,
            allow_cancel=True,
        )

    def handle_edit_note(self, note_id: str | None) -> CommandResult:
        """Handle edit-note command."""
        if not note_id:
            return CommandResult.error(
                "Please provide a note ID.",
                details=["Usage: edit-note <note_id>"],
            )

        try:
            note = self.note_service.get_note(note_id)
        except NoteNotFoundError:
            return CommandResult.error(f"Note {note_id} not found.")

        self._print_section_intro("Edit Note")
        print("Current note:")
        print(Renderer.render_note(note))
        print()

        choice = self._prompt_edit_note_choice(note)
        if choice is None or choice == "0":
            return CommandResult.info("Cancelled.")

        try:
            if choice == "1":
                content = self._prompt_required_value(
                    "New content: ",
                    example="Call the supplier on Friday about the invoice.",
                    allow_cancel=True,
                )
                if content is None:
                    return CommandResult.info("Cancelled.")

                updated_note = self.note_service.update_note(note_id, content=content)
                return CommandResult.success(
                    "Note updated.",
                    data=[updated_note],
                )

            if choice == "2":
                tags = self._prompt_csv_values(
                    "New tags: ",
                    required=False,
                    example="work, urgent, finance",
                    rules=[
                        "Separate multiple tags with commas.",
                        "Press Enter to clear all current tags.",
                    ],
                    allow_cancel=True,
                )
                if tags is None:
                    return CommandResult.info("Cancelled.")

                updated_note = self.note_service.update_note(note_id, tags=tags or [])
                return CommandResult.success(
                    "Note updated.",
                    data=[updated_note],
                )

            return CommandResult.error("Invalid choice.")

        except (ValidationError, ValueError) as error:
            return CommandResult.error(f"Error: {error}")

    def handle_delete_note(self, note_id: str | None) -> CommandResult:
        """Handle delete-note command."""
        if not note_id:
            return CommandResult.error(
                "Please provide a note ID.",
                details=["Usage: delete-note <note_id>"],
            )

        try:
            note = self.note_service.get_note(note_id)
        except NoteNotFoundError:
            return CommandResult.error(f"Note {note_id} not found.")

        self._print_section_intro("Delete Note")
        print("You are about to delete this note:")
        print(Renderer.render_note(note))
        print()

        if not self._confirm_action("Confirm deletion [y/n]: "):
            return CommandResult.info("Cancelled.")

        self.note_service.delete_note(note_id)
        return CommandResult.success("Note deleted.")

    def handle_notes_by_tag(self, args_str: str | None) -> CommandResult:
        """Handle notes-by-tag command."""
        if not args_str:
            return CommandResult.error(
                "Please provide at least one tag.",
                details=["Usage: notes-by-tag [--any|--all] <tag1> [tag2] ..."],
            )

        parts = args_str.split()
        use_all = False

        if parts and parts[0] == "--all":
            use_all = True
            parts = parts[1:]
        elif parts and parts[0] == "--any":
            parts = parts[1:]

        if not parts:
            return CommandResult.error("Please provide at least one tag.")

        mode_label = "ALL" if use_all else "ANY"

        try:
            if use_all:
                results = self.note_service.get_notes_by_all_tags(parts)
            else:
                results = self.note_service.get_notes_by_any_tag(parts)

            if not results:
                return CommandResult.info("No notes found.")

            return CommandResult.info(
                f"Notes with tags: {', '.join(parts)}",
                data=results,
                details=[
                    f"Matching mode: {mode_label}",
                    f"Found {len(results)} note(s):",
                ],
            )

        except ValidationError as error:
            return CommandResult.error(f"Invalid tag: {error}")