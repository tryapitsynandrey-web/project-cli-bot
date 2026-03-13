import pytest

from assistant_bot.utils import fuzzy_match


class TestSimilarity:
    """Tests for string similarity scoring."""

    def test_similarity_identical_strings(self):
        """Identical strings should have similarity of 1.0."""
        assert fuzzy_match.similarity("hello", "hello") == 1.0

    def test_similarity_very_close_strings(self):
        """Very similar strings should score highly."""
        assert fuzzy_match.similarity("add-con", "add-contact") > 0.8

    def test_similarity_partial_match(self):
        """Partial matches should score decently."""
        assert fuzzy_match.similarity("contact", "add-contact") > 0.5

    def test_similarity_prefix_match_boost(self):
        """Prefix matches should be boosted."""
        prefix_sim = fuzzy_match.similarity("add", "add-contact")
        assert prefix_sim > 0

    def test_similarity_completely_different(self):
        """Completely different strings should score low."""
        sim = fuzzy_match.similarity("xyz", "abc")
        assert sim < 0.5

    def test_similarity_empty_strings(self):
        """Empty strings should have zero similarity."""
        assert fuzzy_match.similarity("", "") == 0.0

    def test_similarity_one_empty(self):
        """One empty string should have low similarity."""
        sim = fuzzy_match.similarity("", "hello")
        assert sim < 0.5

    def test_similarity_case_insensitive(self):
        """Similarity should be case-insensitive."""
        lower = fuzzy_match.similarity("hello", "HELLO")
        upper = fuzzy_match.similarity("HELLO", "hello")
        assert lower == upper == 1.0

    def test_similarity_longer_strings(self):
        """Should handle longer strings."""
        sim = fuzzy_match.similarity("contacts-by-tag-edit", "contacts-by-tag")
        assert sim > 0.7


class TestFindClosestMatch:
    """Tests for finding closest matching string."""

    def test_find_closest_exact_match(self):
        """Should find exact match when available."""
        candidates = ["help", "add-contact", "exit"]
        assert fuzzy_match.find_closest_match("help", candidates) == "help"

    def test_find_closest_fuzzy_match(self):
        """Should find closest fuzzy match."""
        candidates = ["add-contact", "list-contacts", "search-contact"]
        assert fuzzy_match.find_closest_match("add-con", candidates) == "add-contact"

    @pytest.mark.parametrize(
        "inp,expected",
        [
            ("add-con", "add-contact"),
            ("list-con", "list-contacts"),
            ("hlp", "help"),
        ],
    )
    def test_find_closest_parametrized_matches(self, inp, expected):
        """Parametrized test for various close matches."""
        candidates = [
            "add-contact", "list-contacts", "search-contact", 
            "help", "exit", "add-note"
        ]
        assert fuzzy_match.find_closest_match(inp, candidates) == expected

    def test_find_closest_empty_input_returns_none(self):
        """Empty input should return None."""
        candidates = ["help", "exit"]
        assert fuzzy_match.find_closest_match("", candidates) is None

    def test_find_closest_empty_candidates_returns_none(self):
        """Empty candidates list should return None."""
        assert fuzzy_match.find_closest_match("help", []) is None

    def test_find_closest_single_candidate(self):
        """Single candidate should be returned if similar enough."""
        # "hel" is similar to "help"
        assert fuzzy_match.find_closest_match("hel", ["help"]) == "help"
        # "xx" is not similar to "help", returns None
        assert fuzzy_match.find_closest_match("xx", ["help"]) is None

    def test_find_closest_case_insensitive(self):
        """Should find match regardless of case."""
        candidates = ["Help", "EXIT", "Add-Contact"]
        assert fuzzy_match.find_closest_match("help", candidates) == "Help"

    def test_find_closest_prefix_preference(self):
        """Should prefer prefix matches when available."""
        candidates = ["add-contact", "extra-add", "add-note"]
        result = fuzzy_match.find_closest_match("add", candidates)
        # Should prefer commands starting with "add"
        assert "add" in result


class TestFindAllSimilar:
    """Tests for finding all similar matches."""

    def test_find_all_similar_prefix_matches(self):
        """Should find all commands with matching prefix."""
        candidates = ["add-contact", "list-contacts", "add-note", "help"]
        similar = fuzzy_match.find_all_similar("add", candidates, threshold=0.1)
        assert "add-contact" in similar
        assert "add-note" in similar
        assert "help" not in similar

    def test_find_all_similar_respects_threshold(self):
        """Should respect similarity threshold."""
        candidates = ["add-contact", "list-contacts", "search-contact"]
        loose = fuzzy_match.find_all_similar("add", candidates, threshold=0.1)
        strict = fuzzy_match.find_all_similar("add", candidates, threshold=0.9)
        # Strict threshold should have fewer or equal results
        assert len(strict) <= len(loose)

    def test_find_all_similar_empty_input(self):
        """Empty input should return empty list."""
        candidates = ["help", "exit"]
        assert fuzzy_match.find_all_similar("", candidates) == []

    def test_find_all_similar_empty_candidates(self):
        """Empty candidates list should return empty."""
        assert fuzzy_match.find_all_similar("help", []) == []

    def test_find_all_similar_returns_list(self):
        """Should always return a list."""
        candidates = ["add-contact", "add-note"]
        result = fuzzy_match.find_all_similar("add", candidates)
        assert isinstance(result, list)

    def test_find_all_similar_substring_match(self):
        """Should find substring matches."""
        candidates = ["add-contact", "list-contacts", "search-contact"]
        similar = fuzzy_match.find_all_similar("contact", candidates, threshold=0.1)
        assert len(similar) > 0
        assert "add-contact" in similar or "list-contacts" in similar

    def test_find_all_similar_no_duplicates(self):
        """Should not return duplicate matches."""
        candidates = ["add-contact", "add-note", "add-tag"]
        similar = fuzzy_match.find_all_similar("add", candidates, threshold=0.0)
        assert len(similar) == len(set(similar))

    def test_find_all_similar_exact_matches_included(self):
        """Should include exact matches in results."""
        candidates = ["help", "add", "exit"]
        similar = fuzzy_match.find_all_similar("help", candidates, threshold=0.5)
        assert "help" in similar

    def test_find_all_similar_case_insensitive(self):
        """Matching should be case-insensitive."""
        candidates = ["Add-Contact", "LIST-CONTACTS"]
        similar = fuzzy_match.find_all_similar("add", candidates, threshold=0.5)
        assert any("add" in cmd.lower() for cmd in similar)
