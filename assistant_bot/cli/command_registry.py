"""Command registry for CLI command dispatching."""

from __future__ import annotations

from collections.abc import Callable

from assistant_bot.cli.parser import Command


CommandHandlerFn = Callable[[Command], bool]


class CommandRegistry:
    """Registry for CLI command handlers."""

    def __init__(self) -> None:
        """Initialize an empty command registry."""
        self._commands: dict[str, CommandHandlerFn] = {}

    def register(self, command_name: str, handler: CommandHandlerFn) -> None:
        """Register a command handler by command name."""
        normalized_name = command_name.strip().lower()

        if not normalized_name:
            raise ValueError("Command name cannot be empty.")

        if normalized_name in self._commands:
            raise ValueError(f"Command '{normalized_name}' is already registered.")

        self._commands[normalized_name] = handler

    def get(self, command_name: str) -> CommandHandlerFn | None:
        """Return a registered handler for a command name."""
        return self._commands.get(command_name.strip().lower())

    def has(self, command_name: str) -> bool:
        """Return whether a command is registered."""
        return command_name.strip().lower() in self._commands

    def names(self) -> list[str]:
        """Return all registered command names sorted alphabetically."""
        return sorted(self._commands)

    def as_dict(self) -> dict[str, CommandHandlerFn]:
        """Return a shallow copy of the registry mapping."""
        return dict(self._commands)