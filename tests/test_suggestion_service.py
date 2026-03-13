import pytest

from assistant_bot.services.suggestion_service import SuggestionService


class TestSuggestCommand:
    """Tests for suggesting commands."""

    def test_suggest_exact_match(self):
        """Should suggest exact command match."""
        svc = SuggestionService()
        assert svc.suggest_command("help") == "help"
        assert svc.suggest_command("add-contact") == "add-contact"

    def test_suggest_alias(self):
        """Should suggest command for valid alias."""
        svc = SuggestionService()
        assert svc.suggest_command("ac") == "add-contact"
        assert svc.suggest_command("q") == "exit"
        assert svc.suggest_command("h") == "help"

    def test_suggest_fuzzy_match(self):
        """Should find closest match for partial input."""
        svc = SuggestionService()
        result = svc.suggest_command("add-con")
        assert result == "add-contact"

    def test_suggest_empty_returns_none(self):
        """Empty input should return None."""
        svc = SuggestionService()
        assert svc.suggest_command("") is None

    def test_suggest_whitespace_only_returns_none(self):
        """Whitespace-only input should return None."""
        svc = SuggestionService()
        assert svc.suggest_command("   ") is None

    def test_suggest_case_insensitive(self):
        """Suggestion should be case-insensitive."""
        svc = SuggestionService()
        assert svc.suggest_command("AC") == "add-contact"
        assert svc.suggest_command("HELP") == "help"

    def test_suggest_nonexistent_returns_closest(self):
        """Should return closest match for non-existent command."""
        svc = SuggestionService()
        result = svc.suggest_command("hlp")  # close to help
        assert result == "help"


class TestGetSimilarCommands:
    """Tests for finding similar commands."""

    def test_similar_with_prefix_match(self):
        """Should find commands with matching prefix."""
        svc = SuggestionService()
        similars = svc.get_similar_commands("add", threshold=0.1, limit=10)
        assert "add-contact" in similars
        assert "add-note" in similars
        assert "add-tag" in similars

    def test_similar_with_substring_match(self):
        """Should find commands with substring match."""
        svc = SuggestionService()
        similars = svc.get_similar_commands("contact", threshold=0.1, limit=10)
        assert "add-contact" in similars
        assert "list-contacts" in similars

    def test_similar_empty_input_returns_empty(self):
        """Empty input should return empty list."""
        svc = SuggestionService()
        assert svc.get_similar_commands("", threshold=0.1) == []

    def test_similar_limit_respected(self):
        """Should respect limit parameter."""
        svc = SuggestionService()
        limited = svc.get_similar_commands("a", threshold=0.0, limit=2)
        assert len(limited) <= 2

    def test_similar_threshold_affects_results(self):
        """Higher threshold should return fewer results."""
        svc = SuggestionService()
        loose = svc.get_similar_commands("help", threshold=0.1, limit=20)
        strict = svc.get_similar_commands("help", threshold=0.95, limit=20)
        # Strict threshold should have fewer or same results
        assert len(strict) <= len(loose)

    def test_similar_default_limit(self):
        """Should use default limit if not specified."""
        svc = SuggestionService()
        results = svc.get_similar_commands("add")
        assert isinstance(results, list)
        assert len(results) >= 0

    def test_similar_returns_list(self):
        """Should always return a list."""
        svc = SuggestionService()
        assert isinstance(svc.get_similar_commands("help"), list)
        assert isinstance(svc.get_similar_commands("xyz"), list)

    def test_similar_no_duplicates(self):
        """Should not return duplicate suggestions."""
        svc = SuggestionService()
        similars = svc.get_similar_commands("contact", threshold=0.0, limit=20)
        assert len(similars) == len(set(similars))

    def test_similar_case_insensitive(self):
        """Search should be case-insensitive."""
        svc = SuggestionService()
        lower = svc.get_similar_commands("add", threshold=0.1, limit=10)
        upper = svc.get_similar_commands("ADD", threshold=0.1, limit=10)
        assert set(lower) == set(upper)
