"""Command handlers for all CLI commands."""

from assistant_bot.cli.help_text import COMMAND_HELP, get_help_text
from assistant_bot.cli.renderer import Renderer
from assistant_bot.domain.exceptions import (
    NoteNotFoundError,
    PersonalAssistantError,
    ValidationError,
)
from assistant_bot.services.birthday_service import BirthdayService
from assistant_bot.services.contact_service import ContactService
from assistant_bot.services.note_service import NoteService
from assistant_bot.services.suggestion_service import SuggestionService


class CommandHandler:
    """Handle CLI commands."""

    def __init__(
        self,
        contact_service: ContactService,
        note_service: NoteService,
        birthday_service: BirthdayService,
        suggestion_service: SuggestionService,
    ) -> None:
        """Initialize command handler services."""
        self.contact_service = contact_service
        self.note_service = note_service
        self.birthday_service = birthday_service
        self.suggestion_service = suggestion_service

    # =========================
    # Internal helper methods
    # =========================

    @staticmethod
    def _parse_csv_values(raw_value: str) -> list[str]:
        """Split comma-separated input into a normalized list of values."""
        return [item.strip() for item in raw_value.split(",") if item.strip()]

    def _select_contact_by_name(self, contact_name: str):
        """Find a contact by name and resolve duplicates via interactive selection."""
        contacts = self.contact_service.get_contacts_by_name(contact_name)

        if not contacts:
            print(Renderer.error(f"No contacts found with name '{contact_name}'."))
            return None

        if len(contacts) == 1:
            return contacts[0]

        print(f"\nFound {len(contacts)} contacts:")
        for index, contact in enumerate(contacts, start=1):
            phones = ", ".join(contact.phone_numbers)
            print(f"{index}. {contact.name} ({phones})")

        choice = input("Select contact number: ").strip()

        try:
            return contacts[int(choice) - 1]
        except (ValueError, IndexError):
            print(Renderer.error("Invalid selection."))
            return None

    @staticmethod
    def _confirm_action(prompt: str = "Type 'yes' to confirm: ") -> bool:
        """Ask user to confirm a destructive action."""
        return input(prompt).strip().lower() == "yes"

    # =========================
    # Contact commands
    # =========================

    def handle_add_contact(self) -> None:
        """Handle add-contact command."""
        print("\n" + Renderer.header("Add New Contact"))

        try:
            name = input("Name (required): ").strip()
            phones_str = input("Phone number(s) - comma-separated (required): ").strip()

            if not name:
                print(Renderer.error("Name is required."))
                return

            phone_numbers = self._parse_csv_values(phones_str)
            if not phone_numbers:
                print(Renderer.error("At least one phone number is required."))
                return

            email = input("Email (optional): ").strip()
            address = input("Address (optional): ").strip()
            birthday = input("Birthday YYYY-MM-DD (optional): ").strip()
            note = input("Note (optional): ").strip()
            tags_str = input("Tags - comma-separated (optional): ").strip()

            tags = self._parse_csv_values(tags_str)

            contact = self.contact_service.add_contact(
                name=name,
                phone_numbers=phone_numbers,
                address=address or None,
                email=email or None,
                birthday=birthday or None,
                note=note or None,
                tags=tags,
            )

            print(Renderer.success(f"Contact added: {contact.name}"))
            print(f"ID: {contact.contact_id}")

        except ValidationError as error:
            print(Renderer.error(f"Validation error: {error}"))
        except ValueError as error:
            print(Renderer.error(f"Invalid input: {error}"))
        except PersonalAssistantError as error:
            print(Renderer.error(f"Error: {error}"))

    def handle_list_contacts(self) -> None:
        """Handle list-contacts command."""
        print("\n" + Renderer.header("All Contacts"))

        contacts = self.contact_service.get_all_contacts()

        if not contacts:
            print(Renderer.info("No contacts found."))
            return

        for contact in contacts:
            print()
            print(Renderer.render_contact(contact))

    def handle_search_contact(self, query: str | None) -> None:
        """Handle search-contact command."""
        if not query:
            print(Renderer.error("Please provide a search query."))
            print("Usage: search-contact <query>")
            return

        print("\n" + Renderer.header(f"Search Results for '{query}'"))

        results = self.contact_service.search_contacts(query)

        if not results:
            print(Renderer.info("No contacts found matching your search."))
            return

        print(f"Found {len(results)} contact(s):\n")
        for contact in results:
            print(Renderer.render_contact(contact))
            print()

    def handle_edit_contact(self, contact_name: str | None = None) -> None:
        """Handle edit-contact command."""
        if not contact_name:
            contact_name = input("Contact name: ").strip()

        if not contact_name:
            print(Renderer.error("Please provide a contact name."))
            return

        contact = self._select_contact_by_name(contact_name)
        if contact is None:
            return

        print("\n" + Renderer.header(f"Edit Contact: {contact.name}"))
        print("Current info:")
        print(Renderer.render_contact(contact))

        print("\nWhat would you like to edit?")
        print("1. Name")
        print("2. Address")
        print("3. Phone numbers")
        print("4. Email")
        print("5. Birthday")
        print("6. Note")
        print("7. Tags")
        print("0. Cancel")

        choice = input("\nChoice (0-7): ").strip()

        try:
            if choice == "1":
                name = input("New name: ").strip()
                self.contact_service.update_contact(contact.contact_id, name=name)
                print(Renderer.success("Contact updated."))

            elif choice == "2":
                address = input("New address: ").strip()
                self.contact_service.update_contact(
                    contact.contact_id,
                    address=address or None,
                )
                print(Renderer.success("Contact updated."))

            elif choice == "3":
                phones_str = input("New phone number(s) (comma-separated): ").strip()
                phones = self._parse_csv_values(phones_str)
                self.contact_service.update_contact(
                    contact.contact_id,
                    phone_numbers=phones,
                )
                print(Renderer.success("Contact updated."))

            elif choice == "4":
                email = input("New email: ").strip()
                self.contact_service.update_contact(
                    contact.contact_id,
                    email=email or None,
                )
                print(Renderer.success("Contact updated."))

            elif choice == "5":
                birthday = input("New birthday (YYYY-MM-DD): ").strip()
                self.contact_service.update_contact(
                    contact.contact_id,
                    birthday=birthday or None,
                )
                print(Renderer.success("Contact updated."))

            elif choice == "6":
                note = input("New note: ").strip()
                self.contact_service.update_contact(
                    contact.contact_id,
                    note=note or None,
                )
                print(Renderer.success("Contact updated."))

            elif choice == "7":
                tags_str = input("New tags (comma-separated): ").strip()
                tags = self._parse_csv_values(tags_str)
                self.contact_service.update_contact(contact.contact_id, tags=tags)
                print(Renderer.success("Contact updated."))

            elif choice == "0":
                print("Cancelled.")

            else:
                print(Renderer.error("Invalid choice."))

        except (ValidationError, ValueError) as error:
            print(Renderer.error(f"Error: {error}"))

    def handle_delete_contact(self, contact_name: str | None = None) -> None:
        """Handle delete-contact command."""
        if not contact_name:
            contact_name = input("Contact name: ").strip()

        if not contact_name:
            print(Renderer.error("Please provide a contact name."))
            return

        contact = self._select_contact_by_name(contact_name)
        if contact is None:
            return

        print("\n" + Renderer.warning(f"Delete contact: {contact.name}"))
        if self._confirm_action():
            self.contact_service.delete_contact(contact.contact_id)
            print(Renderer.success("Contact deleted."))
        else:
            print("Cancelled.")

    def handle_birthdays(self, days_str: str | None = None) -> None:
        """Handle birthdays command."""
        days = 7

        if days_str:
            try:
                parsed_days = int(days_str)
                if parsed_days > 0:
                    days = parsed_days
                else:
                    print(Renderer.warning("Days must be greater than 0. Using default (7)."))
            except ValueError:
                print(Renderer.warning("Invalid days value. Using default (7)."))

        print("\n" + Renderer.header(f"Upcoming Birthdays (next {days} days)"))

        upcoming = self.birthday_service.get_upcoming_birthdays(days)

        if not upcoming:
            print(Renderer.info(f"No birthdays in the next {days} day(s)."))
            return

        for item in upcoming:
            print(f"{Renderer.highlight(item['name'])}: {item['formatted']}")

    # =========================
    # Contact tag commands
    # =========================

    def handle_add_tag(self) -> None:
        """Handle add-tag command for contacts."""
        print("\n" + Renderer.header("Add Tag to Contact"))

        try:
            contact_name = input("Contact name: ").strip()
            if not contact_name:
                print(Renderer.error("Please provide a contact name."))
                return

            contact = self._select_contact_by_name(contact_name)
            if contact is None:
                return

            tags_str = input("Tags to add (comma-separated): ").strip()
            tags = self._parse_csv_values(tags_str)

            if not tags:
                print(Renderer.error("Please provide at least one tag."))
                return

            for tag in tags:
                self.contact_service.add_tag_to_contact(contact.contact_id, tag)

            updated_contact = self.contact_service.get_contact(contact.contact_id)
            print(Renderer.success(f"Tags added to {updated_contact.name}"))
            print(f"Tags: {', '.join(updated_contact.tags)}")

        except (ValidationError, ValueError) as error:
            print(Renderer.error(f"Error: {error}"))

    def handle_edit_tag(self) -> None:
        """Handle edit-tag command for contacts."""
        print("\n" + Renderer.header("Edit Contact Tag"))

        try:
            contact_name = input("Contact name: ").strip()
            if not contact_name:
                print(Renderer.error("Please provide a contact name."))
                return

            contact = self._select_contact_by_name(contact_name)
            if contact is None:
                return

            if not contact.tags:
                print(Renderer.info("This contact has no tags to edit."))
                return

            print("\nCurrent tags:")
            for index, tag in enumerate(contact.tags, start=1):
                print(f"{index}. {tag}")

            old_tag = input("Tag to replace: ").strip()
            new_tag = input("New tag value: ").strip()

            if not old_tag or not new_tag:
                print(Renderer.error("Both old tag and new tag are required."))
                return

            self.contact_service.edit_contact_tag(contact.contact_id, old_tag, new_tag)

            updated_contact = self.contact_service.get_contact(contact.contact_id)
            print(Renderer.success(f"Tag updated for {updated_contact.name}"))
            print(f"Tags: {', '.join(updated_contact.tags)}")

        except (ValidationError, ValueError) as error:
            print(Renderer.error(f"Error: {error}"))

    def handle_delete_tag(self) -> None:
        """Handle delete-tag command for contacts."""
        print("\n" + Renderer.header("Delete Tag from Contact"))

        try:
            contact_name = input("Contact name: ").strip()
            if not contact_name:
                print(Renderer.error("Please provide a contact name."))
                return

            contact = self._select_contact_by_name(contact_name)
            if contact is None:
                return

            if not contact.tags:
                print(Renderer.info("This contact has no tags to delete."))
                return

            print("\nCurrent tags:")
            for tag in contact.tags:
                print(f"- {tag}")

            tags_str = input("Tags to delete (comma-separated): ").strip()
            tags = self._parse_csv_values(tags_str)

            if not tags:
                print(Renderer.error("Please provide at least one tag to delete."))
                return

            for tag in tags:
                self.contact_service.delete_tag_from_contact(contact.contact_id, tag)

            updated_contact = self.contact_service.get_contact(contact.contact_id)
            print(Renderer.success(f"Tags removed from {updated_contact.name}"))

            if updated_contact.tags:
                print(f"Remaining tags: {', '.join(updated_contact.tags)}")
            else:
                print("No tags remaining.")

        except (ValidationError, ValueError) as error:
            print(Renderer.error(f"Error: {error}"))

    def handle_list_tags(self) -> None:
        """Handle list-tags command for contact tags."""
        print("\n" + Renderer.header("All Contact Tags"))

        tag_map: dict[str, int] = {}
        for tag in self.contact_service.get_all_contact_tags():
            tag_map[tag] = 0

        for contact in self.contact_service.get_all_contacts():
            for tag in contact.tags:
                tag_map[tag] = tag_map.get(tag, 0) + 1

        if not tag_map:
            print(Renderer.info("No contact tags in use yet."))
            return

        print(f"Total tags: {len(tag_map)}\n")
        for tag in sorted(tag_map):
            print(f"#{tag} ({tag_map[tag]} contact(s))")

    def handle_view_contacts_by_tag(self, tag: str | None) -> None:
        """Handle contacts-by-tag command."""
        if not tag:
            print(Renderer.error("Please provide a tag name."))
            print("Usage: contacts-by-tag <tag>")
            return

        print("\n" + Renderer.header(f"Contacts with tag: {tag}"))

        try:
            contacts = self.contact_service.get_contacts_by_tag(tag)
        except (ValidationError, ValueError) as error:
            print(Renderer.error(f"Error: {error}"))
            return

        if not contacts:
            print(Renderer.info(f"No contacts found with tag '{tag}'."))
            return

        print(f"Found {len(contacts)} contact(s):\n")
        for contact in contacts:
            print(Renderer.render_contact(contact))
            print()

    # =========================
    # Note commands
    # =========================

    def handle_add_note(self) -> None:
        """Handle add-note command."""
        print("\n" + Renderer.header("Add New Note"))

        try:
            content = input("Note content: ").strip()
            tags_str = input("Tags (comma-separated, optional): ").strip()
            tags = self._parse_csv_values(tags_str)

            note = self.note_service.add_note(content, tags)

            print(Renderer.success("Note added."))
            print(f"ID: {note.note_id}")
            if note.tags:
                print(f"Tags: {', '.join(note.tags)}")

        except ValidationError as error:
            print(Renderer.error(f"Validation error: {error}"))
        except ValueError as error:
            print(Renderer.error(f"Invalid input: {error}"))

    def handle_list_notes(self) -> None:
        """Handle list-notes command."""
        print("\n" + Renderer.header("All Notes"))

        notes = self.note_service.get_all_notes()

        if not notes:
            print(Renderer.info("No notes found."))
            return

        print(f"Total notes: {len(notes)}\n")
        for note in notes:
            print(Renderer.render_note(note))
            print()

    def handle_search_notes(self, query: str | None) -> None:
        """Handle search-notes command."""
        if not query:
            print(Renderer.error("Please provide a search query."))
            print("Usage: search-notes <query>")
            return

        print("\n" + Renderer.header(f"Search Results for '{query}'"))

        results = self.note_service.search_notes(query)

        if not results:
            print(Renderer.info("No notes found matching your search."))
            return

        print(f"Found {len(results)} note(s):\n")
        for note in results:
            print(Renderer.render_note(note))
            print()

    def handle_edit_note(self, note_id: str | None) -> None:
        """Handle edit-note command."""
        if not note_id:
            print(Renderer.error("Please provide a note ID."))
            print("Usage: edit-note <note_id>")
            return

        try:
            note = self.note_service.get_note(note_id)
        except NoteNotFoundError:
            print(Renderer.error(f"Note {note_id} not found."))
            return

        print("\n" + Renderer.header("Edit Note"))
        print("Current content:")
        print(Renderer.render_note(note))

        print("\nWhat would you like to edit?")
        print("1. Content")
        print("2. Tags")
        print("0. Cancel")

        choice = input("\nChoice (0-2): ").strip()

        try:
            if choice == "1":
                content = input("New content: ").strip()
                self.note_service.update_note(note_id, content=content)
                print(Renderer.success("Note updated."))

            elif choice == "2":
                tags_str = input("New tags (comma-separated, optional): ").strip()
                tags = self._parse_csv_values(tags_str)
                self.note_service.update_note(note_id, tags=tags)
                print(Renderer.success("Note updated."))

            elif choice == "0":
                print("Cancelled.")

            else:
                print(Renderer.error("Invalid choice."))

        except (ValidationError, ValueError) as error:
            print(Renderer.error(f"Error: {error}"))

    def handle_delete_note(self, note_id: str | None) -> None:
        """Handle delete-note command."""
        if not note_id:
            print(Renderer.error("Please provide a note ID."))
            print("Usage: delete-note <note_id>")
            return

        try:
            note = self.note_service.get_note(note_id)
        except NoteNotFoundError:
            print(Renderer.error(f"Note {note_id} not found."))
            return

        preview = note.get_preview(50)
        print(f"\nDelete note: '{preview}'?")

        if self._confirm_action():
            self.note_service.delete_note(note_id)
            print(Renderer.success("Note deleted."))
        else:
            print("Cancelled.")

    def handle_notes_by_tag(self, args_str: str | None) -> None:
        """Handle notes-by-tag command."""
        if not args_str:
            print(Renderer.error("Please provide at least one tag."))
            print("Usage: notes-by-tag [--any|--all] <tag1> [tag2] ...")
            return

        parts = args_str.split()
        use_all = False

        if parts and parts[0] == "--all":
            use_all = True
            parts = parts[1:]
        elif parts and parts[0] == "--any":
            parts = parts[1:]

        if not parts:
            print(Renderer.error("Please provide at least one tag."))
            return

        print("\n" + Renderer.header(f"Notes with tags: {', '.join(parts)}"))

        try:
            if use_all:
                results = self.note_service.get_notes_by_all_tags(parts)
                print(f"(Showing notes with ALL {len(parts)} tags)\n")
            else:
                results = self.note_service.get_notes_by_any_tag(parts)
                print(f"(Showing notes with ANY of {len(parts)} tag(s))\n")

            if not results:
                print(Renderer.info("No notes found."))
                return

            print(f"Found {len(results)} note(s):\n")
            for note in results:
                print(Renderer.render_note(note))
                print()

        except ValidationError as error:
            print(Renderer.error(f"Invalid tag: {error}"))

    # =========================
    # System commands
    # =========================

    def handle_help(self, command: str | None = None) -> None:
        """Handle help command."""
        print(get_help_text(command))

    def handle_unknown_command(self, command: str) -> None:
        """Handle unknown command and show the closest suggestion."""
        print(Renderer.error(f"Unknown command: '{command}'"))

        suggestion = self.suggestion_service.suggest_command(command)
        if suggestion:
            print(f"\nDid you mean: {Renderer.highlight(suggestion)}?")
            print(f"Type '{suggestion}' to run it, or 'help' for the menu.")

            usage = COMMAND_HELP.get(suggestion)
            if usage:
                print("\nUsage example:\n")
                print(usage)
        else:
            print("Type 'help' for available commands.")