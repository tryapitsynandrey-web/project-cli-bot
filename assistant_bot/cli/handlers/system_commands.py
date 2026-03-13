"""System-related CLI command handlers."""

from __future__ import annotations

from assistant_bot.cli.handlers.base import HandlerBase
from assistant_bot.cli.help_text import COMMAND_HELP, get_help_text
from assistant_bot.cli.results import CommandResult


class SystemCommandsMixin(HandlerBase):
    """System-related CLI command handlers."""

    def handle_help(self, command: str | None = None) -> CommandResult:
        """Handle help command."""
        if not command:
            return CommandResult.info(get_help_text())

        help_text = get_help_text(command)

        if not help_text.startswith("Unknown command:"):
            return CommandResult.info(help_text)

        suggestion = self.suggestion_service.suggest_command(command)
        similar_commands = self.suggestion_service.get_similar_commands(
            command,
            limit=5,
        )

        if suggestion:
            resolved_help = get_help_text(suggestion)
            details: list[str] = [f"Did you mean: {suggestion}?"]

            if not resolved_help.startswith("Unknown command:"):
                details.append("")
                details.append("Help for suggested command:")
                details.append(resolved_help)

            return CommandResult.warning(
                f"Unknown command in help: '{command}'",
                details=details,
            )

        if similar_commands:
            details = ["Similar commands:"]
            details.extend(f"- {similar_command}" for similar_command in similar_commands)
            details.append("")
            details.append("Type 'help <command>' for command details.")
            return CommandResult.warning(
                f"Unknown command in help: '{command}'",
                details=details,
            )

        return CommandResult.warning(
            f"Unknown command in help: '{command}'",
            details=["Type 'help' for the full command menu."],
        )

    def handle_unknown_command(self, command: str) -> CommandResult:
        """Handle unknown command and show suggestions."""
        suggestion = self.suggestion_service.suggest_command(command)
        similar_commands = self.suggestion_service.get_similar_commands(
            command,
            limit=5,
        )

        if suggestion:
            details = [
                f"Did you mean: {suggestion}?",
                f"Type '{suggestion}' to run it, or 'help {suggestion}' for command details.",
            ]

            usage = COMMAND_HELP.get(suggestion)
            if usage:
                details.append("")
                details.append("Help for suggested command:")
                details.append(usage)

            return CommandResult.error(
                f"Unknown command: '{command}'",
                details=details,
            )

        if similar_commands:
            details = ["Similar commands:"]
            details.extend(f"- {similar_command}" for similar_command in similar_commands)
            details.append("")
            details.append("Type 'help' for the full command menu.")
            return CommandResult.error(
                f"Unknown command: '{command}'",
                details=details,
            )

        return CommandResult.error(
            f"Unknown command: '{command}'",
            details=["Type 'help' for available commands."],
        )