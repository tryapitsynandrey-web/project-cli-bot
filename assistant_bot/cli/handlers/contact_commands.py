"""Contact-related CLI command handlers."""

from __future__ import annotations

from assistant_bot.cli.handlers.base import HandlerBase
from assistant_bot.cli.renderer import Renderer
from assistant_bot.cli.results import CommandResult
from assistant_bot.domain.exceptions import PersonalAssistantError, ValidationError


class ContactCommandsMixin(HandlerBase):
    """Contact-related CLI command handlers."""

    def handle_add_contact(self) -> CommandResult:
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
                return CommandResult.info("Cancelled.")

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
                return CommandResult.info("Cancelled.")

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
                return CommandResult.info("Cancelled.")

            address = self._prompt_optional_value(
                "Address (optional): ",
                example="12 Main Street, Dublin",
                rules=[
                    "Enter a readable postal or street address.",
                ],
                allow_cancel=True,
            )
            if address is None:
                return CommandResult.info("Cancelled.")

            birthday = self._prompt_optional_value(
                "Birthday (optional): ",
                example="1995-08-21",
                rules=[
                    "Birthday format: YYYY-MM-DD",
                ],
                allow_cancel=True,
            )
            if birthday is None:
                return CommandResult.info("Cancelled.")

            note = self._prompt_optional_value(
                "Note (optional): ",
                example="Work contact / Friend from college / Delivery driver",
                rules=[
                    "Use notes for useful context about the contact.",
                ],
                allow_cancel=True,
            )
            if note is None:
                return CommandResult.info("Cancelled.")

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
                return CommandResult.info("Cancelled.")

            contact = self.contact_service.add_contact(
                name=name,
                phone_numbers=phone_numbers,
                address=address or None,
                email=email or None,
                birthday=birthday or None,
                note=note or None,
                tags=tags or [],
            )

            return CommandResult.success(
                f"Contact added: {contact.name}",
                data=[contact],
                details=[f"ID: {contact.contact_id}"],
            )

        except ValidationError as error:
            return CommandResult.error(f"Validation error: {error}")
        except ValueError as error:
            return CommandResult.error(f"Invalid input: {error}")
        except PersonalAssistantError as error:
            return CommandResult.error(f"Error: {error}")

    def handle_list_contacts(self) -> CommandResult:
        """Handle list-contacts command."""
        contacts = self.contact_service.get_all_contacts()

        if not contacts:
            return CommandResult.info("No contacts found.")

        return CommandResult.info(
            "All Contacts",
            data=contacts,
            details=[f"Total contacts: {len(contacts)}"],
        )

    def handle_search_contact(self, query: str | None) -> CommandResult:
        """Handle search-contact command."""
        if not query:
            return CommandResult.error(
                "Please provide a search query.",
                details=["Usage: search-contact <query>"],
            )

        results = self.contact_service.search_contacts(query)

        if not results:
            return CommandResult.info("No contacts found matching your search.")

        return CommandResult.info(
            f"Search Results for '{query}'",
            data=results,
            details=[
                "Search is performed across name, phone, email, address, note, and tags.",
                f"Found {len(results)} contact(s):",
            ],
        )

    def _edit_contact_menu_lines(self, contact) -> list[str]:
        """Build the interactive edit menu for a contact."""
        phones = ", ".join(contact.phone_numbers) if contact.phone_numbers else "(none)"
        tags = ", ".join(contact.tags) if contact.tags else "(none)"

        return [
            "What would you like to edit?",
            f"1. Name       ({contact.name})",
            f"2. Address    ({contact.address or '(none)'})",
            f"3. Phone(s)   ({phones})",
            f"4. Email      ({contact.email or '(none)'})",
            f"5. Birthday   ({contact.birthday or '(none)'})",
            f"6. Note       ({contact.note or '(none)'})",
            f"7. Tags       ({tags})",
            "0. Cancel",
        ]

    def _prompt_edit_contact_choice(self, contact) -> str | None:
        """Prompt the user for which contact field to edit."""
        for line in self._edit_contact_menu_lines(contact):
            print(line)

        return self._prompt_input(
            "\nChoice (0-7): ",
            required=True,
            allow_cancel=True,
        )

    def handle_edit_contact(self, contact_name: str | None = None) -> CommandResult:
        """Handle edit-contact command."""
        if not contact_name:
            contact_name = self._prompt_contact_name(allow_cancel=True)
            if contact_name is None:
                return CommandResult.info("Cancelled.")

        contact = self._select_contact_by_name(contact_name)
        if contact is None:
            return CommandResult.info("Cancelled.")

        self._print_section_intro(f"Edit Contact: {contact.name}")
        print("Current info:")
        print(Renderer.render_contact(contact))
        print()

        choice = self._prompt_edit_contact_choice(contact)
        if choice is None or choice == "0":
            return CommandResult.info("Cancelled.")

        try:
            if choice == "1":
                name = self._prompt_required_value(
                    "New name: ",
                    example="John Smith",
                    allow_cancel=True,
                )
                if name is None:
                    return CommandResult.info("Cancelled.")
                updated_contact = self.contact_service.update_contact(
                    contact.contact_id,
                    name=name,
                )

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
                    return CommandResult.info("Cancelled.")
                updated_contact = self.contact_service.update_contact(
                    contact.contact_id,
                    address=address or None,
                )

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
                    return CommandResult.info("Cancelled.")
                updated_contact = self.contact_service.update_contact(
                    contact.contact_id,
                    phone_numbers=phones,
                )

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
                    return CommandResult.info("Cancelled.")
                updated_contact = self.contact_service.update_contact(
                    contact.contact_id,
                    email=email or None,
                )

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
                    return CommandResult.info("Cancelled.")
                updated_contact = self.contact_service.update_contact(
                    contact.contact_id,
                    birthday=birthday or None,
                )

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
                    return CommandResult.info("Cancelled.")
                updated_contact = self.contact_service.update_contact(
                    contact.contact_id,
                    note=note or None,
                )

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
                    return CommandResult.info("Cancelled.")
                updated_contact = self.contact_service.update_contact(
                    contact.contact_id,
                    tags=tags or [],
                )

            else:
                return CommandResult.error("Invalid choice.")

            return CommandResult.success(
                "Contact updated.",
                data=[updated_contact],
            )

        except (ValidationError, ValueError) as error:
            return CommandResult.error(f"Error: {error}")

    def handle_delete_contact(self, contact_name: str | None = None) -> CommandResult:
        """Handle delete-contact command."""
        if not contact_name:
            contact_name = self._prompt_contact_name(allow_cancel=True)
            if contact_name is None:
                return CommandResult.info("Cancelled.")

        contact = self._select_contact_by_name(contact_name)
        if contact is None:
            return CommandResult.info("Cancelled.")

        self._print_section_intro("Delete Contact")
        print(f"You are about to delete: {contact.name}")
        print(Renderer.render_contact(contact))
        print()

        if not self._confirm_action("Confirm deletion [y/n]: "):
            return CommandResult.info("Cancelled.")

        self.contact_service.delete_contact(contact.contact_id)
        return CommandResult.success("Contact deleted.")

    def handle_birthdays(self, days_str: str | None = None) -> CommandResult:
        """Handle birthdays command."""
        days = 7
        details: list[str] = []

        if days_str:
            try:
                parsed_days = int(days_str)
                if parsed_days > 0:
                    days = parsed_days
                else:
                    details.append("Days must be greater than 0. Using default (7).")
            except ValueError:
                details.append("Invalid days value. Using default (7).")

        upcoming = self.birthday_service.get_upcoming_birthdays(days)

        if not upcoming:
            return CommandResult.info(
                f"Upcoming Birthdays (next {days} days)",
                details=details + [f"No birthdays in the next {days} day(s)."],
            )

        formatted_birthdays = [
            f"{item['name']}: {item['formatted']}"
            for item in upcoming
        ]

        return CommandResult.info(
            f"Upcoming Birthdays (next {days} days)",
            data=formatted_birthdays,
            details=details + [f"Found {len(upcoming)} upcoming birthday(s):"],
        )