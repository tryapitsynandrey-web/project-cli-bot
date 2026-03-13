"""Contact tag-related CLI command handlers."""

from __future__ import annotations

from assistant_bot.cli.handlers.base import HandlerBase
from assistant_bot.cli.results import CommandResult
from assistant_bot.domain.exceptions import ValidationError


class ContactTagCommandsMixin(HandlerBase):
    """Contact tag-related CLI command handlers."""

    @staticmethod
    def _format_tags_line(tags: list[str]) -> str:
        """Format a contact tag list for display."""
        return ", ".join(tags) if tags else "(none)"

    def _print_current_tags(self, tags: list[str]) -> None:
        """Print the current contact tags."""
        print("Current tags:")
        print(self._format_tags_line(tags))
        print()

    def _print_indexed_tags(self, tags: list[str]) -> None:
        """Print indexed tags for interactive selection."""
        print("Current tags:")
        for index, tag in enumerate(tags, start=1):
            print(f"{index}. {tag}")
        print()

    def handle_add_tag(self) -> CommandResult:
        """Handle add-tag command for contacts."""
        self._print_section_intro(
            "Add Tag to Contact",
            "Add one or more tags to an existing contact.",
        )

        try:
            contact_name = self._prompt_contact_name(allow_cancel=True)
            if contact_name is None:
                return CommandResult.info("Cancelled.")

            contact = self._select_contact_by_name(contact_name)
            if contact is None:
                return CommandResult.info("Cancelled.")

            self._print_current_tags(contact.tags)

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
                return CommandResult.info("Cancelled.")

            for tag in tags:
                self.contact_service.add_tag_to_contact(contact.contact_id, tag)

            updated_contact = self.contact_service.get_contact(contact.contact_id)
            return CommandResult.success(
                f"Tags added to {updated_contact.name}",
                data=[updated_contact],
                details=[
                    f"Current tags: {self._format_tags_line(updated_contact.tags)}",
                ],
            )

        except (ValidationError, ValueError) as error:
            return CommandResult.error(f"Error: {error}")

    def handle_edit_tag(self) -> CommandResult:
        """Handle edit-tag command for contacts."""
        self._print_section_intro(
            "Edit Contact Tag",
            "Replace one existing tag with a new value.",
        )

        try:
            contact_name = self._prompt_contact_name(allow_cancel=True)
            if contact_name is None:
                return CommandResult.info("Cancelled.")

            contact = self._select_contact_by_name(contact_name)
            if contact is None:
                return CommandResult.info("Cancelled.")

            if not contact.tags:
                return CommandResult.info("This contact has no tags to edit.")

            self._print_indexed_tags(contact.tags)

            self._print_hint(
                "You can enter the existing tag name or its number from the list above."
            )
            old_tag_input = self._prompt_required_value(
                "Tag to replace: ",
                example="1 or work",
                allow_cancel=True,
            )
            if old_tag_input is None:
                return CommandResult.info("Cancelled.")

            if old_tag_input.isdigit():
                selected_index = int(old_tag_input) - 1
                if selected_index < 0 or selected_index >= len(contact.tags):
                    return CommandResult.error("Invalid tag number.")
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
                return CommandResult.info("Cancelled.")

            self.contact_service.edit_contact_tag(contact.contact_id, old_tag, new_tag)

            updated_contact = self.contact_service.get_contact(contact.contact_id)
            return CommandResult.success(
                f"Tag updated for {updated_contact.name}",
                data=[updated_contact],
                details=[
                    f"Current tags: {self._format_tags_line(updated_contact.tags)}",
                ],
            )

        except (ValidationError, ValueError) as error:
            return CommandResult.error(f"Error: {error}")

    def handle_delete_tag(self) -> CommandResult:
        """Handle delete-tag command for contacts."""
        self._print_section_intro(
            "Delete Tag from Contact",
            "Remove one or more tags from an existing contact.",
        )

        try:
            contact_name = self._prompt_contact_name(allow_cancel=True)
            if contact_name is None:
                return CommandResult.info("Cancelled.")

            contact = self._select_contact_by_name(contact_name)
            if contact is None:
                return CommandResult.info("Cancelled.")

            if not contact.tags:
                return CommandResult.info("This contact has no tags to delete.")

            self._print_indexed_tags(contact.tags)

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
                return CommandResult.info("Cancelled.")

            if not self._confirm_action("Confirm tag deletion [y/n]: "):
                return CommandResult.info("Cancelled.")

            for tag in tags:
                self.contact_service.delete_tag_from_contact(contact.contact_id, tag)

            updated_contact = self.contact_service.get_contact(contact.contact_id)
            return CommandResult.success(
                f"Tags removed from {updated_contact.name}",
                data=[updated_contact],
                details=[
                    f"Remaining tags: {self._format_tags_line(updated_contact.tags)}",
                ],
            )

        except (ValidationError, ValueError) as error:
            return CommandResult.error(f"Error: {error}")

    def handle_list_tags(self) -> CommandResult:
        """Handle list-tags command for contact tags."""
        tag_map: dict[str, int] = {}

        for tag in self.contact_service.get_all_contact_tags():
            tag_map[tag] = 0

        for contact in self.contact_service.get_all_contacts():
            for tag in contact.tags:
                tag_map[tag] = tag_map.get(tag, 0) + 1

        if not tag_map:
            return CommandResult.info("No contact tags in use yet.")

        sorted_tags = sorted(
            tag_map.items(),
            key=lambda item: (-item[1], item[0]),
        )

        return CommandResult.info(
            "All Contact Tags",
            data=sorted_tags,
            details=[
                "Tags are sorted by usage count and then alphabetically.",
                f"Total tags: {len(sorted_tags)}",
            ],
        )

    def handle_view_contacts_by_tag(self, tag: str | None) -> CommandResult:
        """Handle contacts-by-tag command."""
        if not tag:
            return CommandResult.error(
                "Please provide a tag name.",
                details=["Usage: contacts-by-tag <tag>"],
            )

        try:
            contacts = self.contact_service.get_contacts_by_tag(tag)
        except (ValidationError, ValueError) as error:
            return CommandResult.error(f"Error: {error}")

        if not contacts:
            return CommandResult.info(f"No contacts found with tag '{tag}'.")

        return CommandResult.info(
            f"Contacts with tag: {tag}",
            data=contacts,
            details=[f"Found {len(contacts)} contact(s):"],
        )