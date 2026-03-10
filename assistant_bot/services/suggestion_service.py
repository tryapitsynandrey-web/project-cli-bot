"""Command suggestion service for typo correction."""

from assistant_bot.cli.parser import CommandParser
from assistant_bot.utils.fuzzy_match import find_all_similar, find_closest_match


class SuggestionService:
    """Service for suggesting valid commands from user input."""

    @staticmethod
    def _command_candidates() -> list[str]:
        """Return all command tokens available for matching."""
        return CommandParser.get_all_command_tokens()

    def suggest_command(self, user_input: str, threshold: float = 0.6) -> str | None:
        """Return the closest matching canonical command."""
        if not user_input or not user_input.strip():
            return None

        raw_match = find_closest_match(
            user_input.strip().lower(),
            self._command_candidates(),
            threshold,
        )
        if raw_match is None:
            return None

        return CommandParser.normalize_command_name(raw_match)

    def get_similar_commands(
        self,
        user_input: str,
        threshold: float = 0.5,
        limit: int = 3,
    ) -> list[str]:
        """Return multiple similar canonical commands."""
        if not user_input or not user_input.strip():
            return []

        raw_matches = find_all_similar(
            user_input.strip().lower(),
            self._command_candidates(),
            threshold,
        )

        canonical_matches: list[str] = []
        seen: set[str] = set()

        for match in raw_matches:
            canonical = CommandParser.normalize_command_name(match)
            if canonical in seen:
                continue
            canonical_matches.append(canonical)
            seen.add(canonical)

        return canonical_matches[:limit]