#!/usr/bin/env python3
"""Entry point for the Personal Assistant CLI application."""

from __future__ import annotations

from assistant_bot.app import PersonalAssistant


def main() -> None:
    """Run the Personal Assistant application."""
    PersonalAssistant().run()


if __name__ == "__main__":
    main()