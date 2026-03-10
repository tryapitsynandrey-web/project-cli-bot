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

    @staticmethod
    def _print_hint(message: str) -> None:
        """Print a dimmed helper hint."""
        print(Renderer.dim(message))

    def _print_prompt_meta(
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
                self._print_hint(rule)

        if example:
            self._print_hint(f"Example: {example}")

        if optional:
            self._print_hint("Press Enter to skip this field.")

        if allow_cancel:
            self._print_hint("Type 'cancel' to cancel this action.")

    @staticmethod
    def _print_section_intro(title: str, description: str | None = None) -> None:
        """Print a section header with an optional short description."""
        print("\n" + Renderer.header(title))
        if description:
            print(Renderer.dim(description))

    @staticmethod
    def _normalize_user_input(value: str) -> str:
        """Normalize raw user input."""
        return value.strip()

    def _prompt_input(
        self,
        prompt: str,
        *,
        required: bool = False,
        allow_cancel: bool = False,
    ) -> str | None:
        """Prompt the user for input with optional required and cancel behavior."""
        while True:
            value = self._normalize_user_input(input(prompt))

            if allow_cancel and value.lower() == "cancel":
                return None

            if required and not value:
                print(Renderer.error("This field is required."))
                continue

            return value

    def _prompt_required_value(
        self,
        prompt: str,
        *,
        example: str | None = None,
        rules: list[str] | None = None,
        allow_cancel: bool = False,
    ) -> str | None:
        """Prompt for a required value."""
        self._print_prompt_meta(
            example=example,
            rules=rules,
            optional=False,
            allow_cancel=allow_cancel,
        )
        return self._prompt_input(
            prompt,
            required=True,
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
        self._print_prompt_meta(
            example=example,
            rules=rules,
            optional=True,
            allow_cancel=allow_cancel,
        )
        return self._prompt_input(
            prompt,
            required=False,
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
        self._print_prompt_meta(
            example=example,
            rules=rules,
            optional=not required,
            allow_cancel=allow_cancel,
        )

        while True:
            raw_value = self._prompt_input(
                prompt,
                required=required,
                allow_cancel=allow_cancel,
            )

            if raw_value is None:
                return None

            values = self._parse_csv_values(raw_value)

            if required and not values:
                print(Renderer.error("Please provide at least one value."))
                continue

            return values

    def _prompt_contact_name(
        self,
        *,
        prompt: str = "Contact name: ",
        allow_cancel: bool = False,
    ) -> str | None:
        """Prompt for a contact name."""
        return self._prompt_required_value(
            prompt,
            example="John Smith",
            allow_cancel=allow_cancel,
        )

    @staticmethod
    def _format_contact_choice(contact) -> str:
        """Format one contact row for interactive selection."""
        phones = ", ".join(contact.phone_numbers) if contact.phone_numbers else "(none)"
        email = contact.email if contact.email else "(no email)"
        return f"{contact.name} | {phones} | {email}"

    def _select_from_list(
        self,
        items: list,
        *,
        item_label: str,
        formatter,
    ):
        """Let the user select one item from a list."""
        if not items:
            return None

        if len(items) == 1:
            return items[0]

        print(f"\nFound {len(items)} {item_label}:")
        for index, item in enumerate(items, start=1):
            print(f"{index}. {formatter(item)}")

        while True:
            choice = self._prompt_input(
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

    def _select_from_contacts(self, contacts: list):
        """Let the user select one contact from a list."""
        return self._select_from_list(
            contacts,
            item_label="contacts",
            formatter=self._format_contact_choice,
        )

    def _select_contact_by_name(self, contact_name: str):
        """Find a contact by name and resolve duplicates via interactive selection."""
        contacts = self.contact_service.get_contacts_by_name(contact_name)

        if not contacts:
            print(Renderer.error(f"No contacts found with name '{contact_name}'."))
            return None

        return self._select_from_contacts(contacts)

    def _confirm_action(self, prompt: str = "Confirm action [y/n]: ") -> bool:
        """Ask the user to confirm an action."""
        while True:
            answer = self._normalize_user_input(input(prompt)).lower()

            if answer in {"y", "yes"}:
                return True
            if answer in {"n", "no"}:
                return False

            print(Renderer.error("Please enter 'y'/'yes' or 'n'/'no'."))

        # =========================
    # Contact commands
    # =========================

    def handle_add_contact(self) -> None:
        """Handle add-contact command."""
        self._print_section_intro(
            "Add New Contact",
            "Required fields: name and at least one phone number.",
        )

        try:
            name = self._prompt_required_value(
                "Name (required): ",
                example="John Smith",
                rules=[
                    "Enter the full contact name.",
                ],
                allow_cancel=True,
            )
            if name is None:
                print("Cancelled.")
                return

            phone_numbers = self._prompt_csv_values(
                "Phone number(s) (required): ",
                required=True,
                example="+353830573745, +353851112223",
                rules=[
                    "Use real valid phone numbers.",
                    "Preferred format: international format with country code.",
                    "Separate multiple numbers with commas.",
                ],
                allow_cancel=True,
            )
            if phone_numbers is None:
                print("Cancelled.")
                return

            email = self._prompt_optional_value(
                "Email (optional): ",
                example="john.smith@gmail.com",
                rules=[
                    "Use a real valid email address.",
                    "Fake or test domains such as example.com or test.com are rejected.",
                ],
                allow_cancel=True,
            )
            if email is None:
                print("Cancelled.")
                return

            address = self._prompt_optional_value(
                "Address (optional): ",
                example="12 Main Street, Dublin",
                rules=[
                    "Enter a readable postal or street address.",
                ],
                allow_cancel=True,
            )
            if address is None:
                print("Cancelled.")
                return

            birthday = self._prompt_optional_value(
                "Birthday (optional): ",
                example="1995-08-21",
                rules=[
                    "Birthday format: YYYY-MM-DD",
                ],
                allow_cancel=True,
            )
            if birthday is None:
                print("Cancelled.")
                return

            note = self._prompt_optional_value(
                "Note (optional): ",
                example="Work contact / Friend from college / Delivery driver",
                rules=[
                    "Use notes for useful context about the contact.",
                ],
                allow_cancel=True,
            )
            if note is None:
                print("Cancelled.")
                return

            tags = self._prompt_csv_values(
                "Tags (optional): ",
                required=False,
                example="work, important, family",
                rules=[
                    "Tags are optional and will be normalized automatically.",
                    "Separate multiple tags with commas.",
                ],
                allow_cancel=True,
            )
            if tags is None:
                print("Cancelled.")
                return

            contact = self.contact_service.add_contact(
                name=name,
                phone_numbers=phone_numbers,
                address=address or None,
                email=email or None,
                birthday=birthday or None,
                note=note or None,
                tags=tags or [],
            )

            print(Renderer.success(f"Contact added: {contact.name}"))
            print(f"ID: {contact.contact_id}")
            print()
            print(Renderer.render_contact(contact))

        except ValidationError as error:
            print(Renderer.error(f"Validation error: {error}"))
        except ValueError as error:
            print(Renderer.error(f"Invalid input: {error}"))
        except PersonalAssistantError as error:
            print(Renderer.error(f"Error: {error}"))

    def handle_list_contacts(self) -> None:
        """Handle list-contacts command."""
        self._print_section_intro("All Contacts")

        contacts = self.contact_service.get_all_contacts()

        if not contacts:
            print(Renderer.info("No contacts found."))
            return

        print(f"Total contacts: {len(contacts)}\n")
        for contact in contacts:
            print(Renderer.render_contact(contact))
            print()

    def handle_search_contact(self, query: str | None) -> None:
        """Handle search-contact command."""
        if not query:
            print(Renderer.error("Please provide a search query."))
            print("Usage: search-contact <query>")
            return

        self._print_section_intro(
            f"Search Results for '{query}'",
            "Search is performed across name, phone, email, address, note, and tags.",
        )

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
            contact_name = self._prompt_contact_name(allow_cancel=True)
            if contact_name is None:
                print("Cancelled.")
                return

        contact = self._select_contact_by_name(contact_name)
        if contact is None:
            return

        self._print_section_intro(f"Edit Contact: {contact.name}")
        print("Current info:")
        print(Renderer.render_contact(contact))
        print()

        print("What would you like to edit?")
        print(f"1. Name       ({contact.name})")
        print(f"2. Address    ({contact.address or '(none)'})")
        print(
            f"3. Phone(s)   ({', '.join(contact.phone_numbers) if contact.phone_numbers else '(none)'})"
        )
        print(f"4. Email      ({contact.email or '(none)'})")
        print(f"5. Birthday   ({contact.birthday or '(none)'})")
        print(f"6. Note       ({contact.note or '(none)'})")
        print(f"7. Tags       ({', '.join(contact.tags) if contact.tags else '(none)'})")
        print("0. Cancel")

        choice = input("\nChoice (0-7): ").strip()

        try:
            if choice == "1":
                name = self._prompt_required_value(
                    "New name: ",
                    example="John Smith",
                    allow_cancel=True,
                )
                if name is None:
                    print("Cancelled.")
                    return
                self.contact_service.update_contact(contact.contact_id, name=name)
                print(Renderer.success("Contact updated."))

            elif choice == "2":
                address = self._prompt_optional_value(
                    "New address: ",
                    example="12 Main Street, Dublin",
                    rules=[
                        "Press Enter to clear the current address.",
                    ],
                    allow_cancel=True,
                )
                if address is None:
                    print("Cancelled.")
                    return
                self.contact_service.update_contact(
                    contact.contact_id,
                    address=address or None,
                )
                print(Renderer.success("Contact updated."))

            elif choice == "3":
                phones = self._prompt_csv_values(
                    "New phone number(s): ",
                    required=True,
                    example="+353830573745, +353851112223",
                    rules=[
                        "Use real valid phone numbers.",
                        "Preferred format: international format with country code.",
                        "Separate multiple numbers with commas.",
                    ],
                    allow_cancel=True,
                )
                if phones is None:
                    print("Cancelled.")
                    return
                self.contact_service.update_contact(
                    contact.contact_id,
                    phone_numbers=phones,
                )
                print(Renderer.success("Contact updated."))

            elif choice == "4":
                email = self._prompt_optional_value(
                    "New email: ",
                    example="john.smith@gmail.com",
                    rules=[
                        "Press Enter to clear the current email.",
                        "Fake or test domains such as example.com or test.com are rejected.",
                    ],
                    allow_cancel=True,
                )
                if email is None:
                    print("Cancelled.")
                    return
                self.contact_service.update_contact(
                    contact.contact_id,
                    email=email or None,
                )
                print(Renderer.success("Contact updated."))

            elif choice == "5":
                birthday = self._prompt_optional_value(
                    "New birthday: ",
                    example="1995-08-21",
                    rules=[
                        "Birthday format: YYYY-MM-DD",
                        "Press Enter to clear the current birthday.",
                    ],
                    allow_cancel=True,
                )
                if birthday is None:
                    print("Cancelled.")
                    return
                self.contact_service.update_contact(
                    contact.contact_id,
                    birthday=birthday or None,
                )
                print(Renderer.success("Contact updated."))

            elif choice == "6":
                note = self._prompt_optional_value(
                    "New note: ",
                    example="Work contact / Friend from college / Delivery driver",
                    rules=[
                        "Press Enter to clear the current note.",
                    ],
                    allow_cancel=True,
                )
                if note is None:
                    print("Cancelled.")
                    return
                self.contact_service.update_contact(
                    contact.contact_id,
                    note=note or None,
                )
                print(Renderer.success("Contact updated."))

            elif choice == "7":
                tags = self._prompt_csv_values(
                    "New tags: ",
                    required=False,
                    example="work, important, family",
                    rules=[
                        "Separate multiple tags with commas.",
                        "Press Enter to clear all current tags.",
                    ],
                    allow_cancel=True,
                )
                if tags is None:
                    print("Cancelled.")
                    return
                self.contact_service.update_contact(
                    contact.contact_id,
                    tags=tags or [],
                )
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
            contact_name = self._prompt_contact_name(allow_cancel=True)
            if contact_name is None:
                print("Cancelled.")
                return

        contact = self._select_contact_by_name(contact_name)
        if contact is None:
            return

        self._print_section_intro("Delete Contact")
        print(Renderer.warning(f"You are about to delete: {contact.name}"))
        print(Renderer.render_contact(contact))
        print()

        if self._confirm_action("Confirm deletion [y/n]: "):
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
                    print(
                        Renderer.warning(
                            "Days must be greater than 0. Using default (7)."
                        )
                    )
            except ValueError:
                print(Renderer.warning("Invalid days value. Using default (7)."))

        self._print_section_intro(f"Upcoming Birthdays (next {days} days)")

        upcoming = self.birthday_service.get_upcoming_birthdays(days)

        if not upcoming:
            print(Renderer.info(f"No birthdays in the next {days} day(s)."))
            return

        print(f"Found {len(upcoming)} upcoming birthday(s):\n")
        for item in upcoming:
            print(f"{Renderer.highlight(item['name'])}: {item['formatted']}")

    # =========================
    # Contact tag commands
    # =========================

    def handle_add_tag(self) -> None:
        """Handle add-tag command for contacts."""
        self._print_section_intro(
            "Add Tag to Contact",
            "Add one or more tags to an existing contact.",
        )

        try:
            contact_name = self._prompt_contact_name(allow_cancel=True)
            if contact_name is None:
                print("Cancelled.")
                return

            contact = self._select_contact_by_name(contact_name)
            if contact is None:
                return

            print("Current tags:")
            print(", ".join(contact.tags) if contact.tags else "(none)")
            print()

            tags = self._prompt_csv_values(
                "Tags to add: ",
                required=True,
                example="work, important, family",
                rules=[
                    "Separate multiple tags with commas.",
                    "Tags are normalized automatically.",
                ],
                allow_cancel=True,
            )
            if tags is None:
                print("Cancelled.")
                return

            for tag in tags:
                self.contact_service.add_tag_to_contact(contact.contact_id, tag)

            updated_contact = self.contact_service.get_contact(contact.contact_id)
            print(Renderer.success(f"Tags added to {updated_contact.name}"))
            print(
                f"Current tags: {', '.join(updated_contact.tags) if updated_contact.tags else '(none)'}"
            )

        except (ValidationError, ValueError) as error:
            print(Renderer.error(f"Error: {error}"))

    def handle_edit_tag(self) -> None:
        """Handle edit-tag command for contacts."""
        self._print_section_intro(
            "Edit Contact Tag",
            "Replace one existing tag with a new value.",
        )

        try:
            contact_name = self._prompt_contact_name(allow_cancel=True)
            if contact_name is None:
                print("Cancelled.")
                return

            contact = self._select_contact_by_name(contact_name)
            if contact is None:
                return

            if not contact.tags:
                print(Renderer.info("This contact has no tags to edit."))
                return

            print("Current tags:")
            for index, tag in enumerate(contact.tags, start=1):
                print(f"{index}. {tag}")
            print()

            self._print_hint(
                "You can enter the existing tag name or its number from the list above."
            )
            old_tag_input = self._prompt_required_value(
                "Tag to replace: ",
                example="1 or work",
                allow_cancel=True,
            )
            if old_tag_input is None:
                print("Cancelled.")
                return

            if old_tag_input.isdigit():
                selected_index = int(old_tag_input) - 1
                if selected_index < 0 or selected_index >= len(contact.tags):
                    print(Renderer.error("Invalid tag number."))
                    return
                old_tag = contact.tags[selected_index]
            else:
                old_tag = old_tag_input

            new_tag = self._prompt_required_value(
                "New tag value: ",
                example="client",
                rules=[
                    "Tag values are normalized automatically.",
                ],
                allow_cancel=True,
            )
            if new_tag is None:
                print("Cancelled.")
                return

            self.contact_service.edit_contact_tag(contact.contact_id, old_tag, new_tag)

            updated_contact = self.contact_service.get_contact(contact.contact_id)
            print(Renderer.success(f"Tag updated for {updated_contact.name}"))
            print(
                f"Current tags: {', '.join(updated_contact.tags) if updated_contact.tags else '(none)'}"
            )

        except (ValidationError, ValueError) as error:
            print(Renderer.error(f"Error: {error}"))

    def handle_delete_tag(self) -> None:
        """Handle delete-tag command for contacts."""
        self._print_section_intro(
            "Delete Tag from Contact",
            "Remove one or more tags from an existing contact.",
        )

        try:
            contact_name = self._prompt_contact_name(allow_cancel=True)
            if contact_name is None:
                print("Cancelled.")
                return

            contact = self._select_contact_by_name(contact_name)
            if contact is None:
                return

            if not contact.tags:
                print(Renderer.info("This contact has no tags to delete."))
                return

            print("Current tags:")
            for index, tag in enumerate(contact.tags, start=1):
                print(f"{index}. {tag}")
            print()

            tags = self._prompt_csv_values(
                "Tags to delete: ",
                required=True,
                example="work, family",
                rules=[
                    "Separate multiple tags with commas.",
                    "Tags must match existing contact tags.",
                ],
                allow_cancel=True,
            )
            if tags is None:
                print("Cancelled.")
                return

            if not self._confirm_action("Confirm tag deletion [y/n]: "):
                print("Cancelled.")
                return

            for tag in tags:
                self.contact_service.delete_tag_from_contact(contact.contact_id, tag)

            updated_contact = self.contact_service.get_contact(contact.contact_id)
            print(Renderer.success(f"Tags removed from {updated_contact.name}"))

            if updated_contact.tags:
                print(f"Remaining tags: {', '.join(updated_contact.tags)}")
            else:
                print("Remaining tags: (none)")

        except (ValidationError, ValueError) as error:
            print(Renderer.error(f"Error: {error}"))

    def handle_list_tags(self) -> None:
        """Handle list-tags command for contact tags."""
        self._print_section_intro(
            "All Contact Tags",
            "Tags are sorted by usage count and then alphabetically.",
        )

        tag_map: dict[str, int] = {}
        for tag in self.contact_service.get_all_contact_tags():
            tag_map[tag] = 0

        for contact in self.contact_service.get_all_contacts():
            for tag in contact.tags:
                tag_map[tag] = tag_map.get(tag, 0) + 1

        if not tag_map:
            print(Renderer.info("No contact tags in use yet."))
            return

        sorted_tags = sorted(
            tag_map.items(),
            key=lambda item: (-item[1], item[0]),
        )

        print(f"Total tags: {len(sorted_tags)}\n")
        for tag, count in sorted_tags:
            print(f"#{tag} ({count} contact(s))")

    def handle_view_contacts_by_tag(self, tag: str | None) -> None:
        """Handle contacts-by-tag command."""
        if not tag:
            print(Renderer.error("Please provide a tag name."))
            print("Usage: contacts-by-tag <tag>")
            return

        self._print_section_intro(f"Contacts with tag: {tag}")

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
                print("Cancelled.")
                return

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
                print("Cancelled.")
                return

            note = self.note_service.add_note(content, tags or [])

            print(Renderer.success("Note added."))
            print(f"ID: {note.note_id}")
            print()
            print(Renderer.render_note(note))

        except ValidationError as error:
            print(Renderer.error(f"Validation error: {error}"))
        except ValueError as error:
            print(Renderer.error(f"Invalid input: {error}"))

    def handle_list_notes(self) -> None:
        """Handle list-notes command."""
        self._print_section_intro("All Notes")

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

        self._print_section_intro(
            f"Search Results for '{query}'",
            "Search is performed across note content.",
        )

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

        self._print_section_intro("Edit Note")
        print("Current note:")
        print(Renderer.render_note(note))
        print()

        print("What would you like to edit?")
        print(f"1. Content  ({note.get_preview(50)})")
        print(f"2. Tags     ({', '.join(note.tags) if note.tags else '(none)'})")
        print("0. Cancel")

        choice = input("\nChoice (0-2): ").strip()

        try:
            if choice == "1":
                content = self._prompt_required_value(
                    "New content: ",
                    example="Call the supplier on Friday about the invoice.",
                    allow_cancel=True,
                )
                if content is None:
                    print("Cancelled.")
                    return

                self.note_service.update_note(note_id, content=content)
                print(Renderer.success("Note updated."))

            elif choice == "2":
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
                    print("Cancelled.")
                    return

                self.note_service.update_note(note_id, tags=tags or [])
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

        self._print_section_intro("Delete Note")
        print(Renderer.warning("You are about to delete this note:"))
        print(Renderer.render_note(note))
        print()

        if self._confirm_action("Confirm deletion [y/n]: "):
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

        mode_label = "ALL" if use_all else "ANY"
        self._print_section_intro(
            f"Notes with tags: {', '.join(parts)}",
            f"Matching mode: {mode_label}",
        )

        try:
            if use_all:
                results = self.note_service.get_notes_by_all_tags(parts)

            else:
                results = self.note_service.get_notes_by_any_tag(parts)
                
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
        if not command:
            print(get_help_text())
            return

        help_text = get_help_text(command)

        if not help_text.startswith("Unknown command:"):
            print(help_text)
            return

        print(Renderer.error(f"Unknown command in help: '{command}'"))

        suggestion = self.suggestion_service.suggest_command(command)
        similar_commands = self.suggestion_service.get_similar_commands(
            command,
            limit=5,
        )

        if suggestion:
            print(f"\nDid you mean: {Renderer.highlight(suggestion)}?")
            resolved_help = get_help_text(suggestion)
            if not resolved_help.startswith("Unknown command:"):
                print("\nHelp for suggested command:\n")
                print(resolved_help)
            return

        if similar_commands:
            print("\nSimilar commands:")
            for similar_command in similar_commands:
                print(f"- {similar_command}")
            print("\nType 'help <command>' for command details.")
            return

        print("Type 'help' for the full command menu.")

    def handle_unknown_command(self, command: str) -> None:
        """Handle unknown command and show suggestions."""
        print(Renderer.error(f"Unknown command: '{command}'"))

        suggestion = self.suggestion_service.suggest_command(command)
        similar_commands = self.suggestion_service.get_similar_commands(
            command,
            limit=5,
        )

        if suggestion:
            print(f"\nDid you mean: {Renderer.highlight(suggestion)}?")
            print(
                f"Type '{suggestion}' to run it, or 'help {suggestion}' for command details."
            )

            usage = COMMAND_HELP.get(suggestion)
            if usage:
                print("\nHelp for suggested command:\n")
                print(usage)
            return

        if similar_commands:
            print("\nSimilar commands:")
            for similar_command in similar_commands:
                print(f"- {similar_command}")
            print("\nType 'help' for the full command menu.")
            return

        print("Type 'help' for available commands.")