"""Package entry point for the Personal Assistant CLI application."""

from assistant_bot.app import PersonalAssistant


def main() -> None:
    """Run the Personal Assistant application."""
    app = PersonalAssistant()
    app.run()


if __name__ == "__main__":
    main()