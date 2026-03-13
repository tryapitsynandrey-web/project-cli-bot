"""Structured command results for CLI handlers."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass(slots=True)
class CommandResult:
    """Represent the outcome of a command handler execution."""

    status: str
    message: str | None = None
    data: Any = None
    details: list[str] = field(default_factory=list)

    @classmethod
    def success(
        cls,
        message: str | None = None,
        *,
        data: Any = None,
        details: list[str] | None = None,
    ) -> "CommandResult":
        """Create a success result."""
        return cls(
            status="success",
            message=message,
            data=data,
            details=details or [],
        )

    @classmethod
    def error(
        cls,
        message: str,
        *,
        data: Any = None,
        details: list[str] | None = None,
    ) -> "CommandResult":
        """Create an error result."""
        return cls(
            status="error",
            message=message,
            data=data,
            details=details or [],
        )

    @classmethod
    def info(
        cls,
        message: str,
        *,
        data: Any = None,
        details: list[str] | None = None,
    ) -> "CommandResult":
        """Create an informational result."""
        return cls(
            status="info",
            message=message,
            data=data,
            details=details or [],
        )

    @classmethod
    def warning(
        cls,
        message: str,
        *,
        data: Any = None,
        details: list[str] | None = None,
    ) -> "CommandResult":
        """Create a warning result."""
        return cls(
            status="warning",
            message=message,
            data=data,
            details=details or [],
        )