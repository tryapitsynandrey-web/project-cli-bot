import pytest

from assistant_bot.utils import text_utils


class TestTruncate:
    """Tests for text truncation."""

    def test_truncate_short_text(self):
        """Text shorter than max should be unchanged."""
        assert text_utils.truncate("hello", 10) == "hello"

    def test_truncate_exact_length(self):
        """Text at exact length should be unchanged."""
        assert text_utils.truncate("hello", 5) == "hello"

    def test_truncate_long_text(self):
        """Long text should be truncated with ellipsis."""
        assert text_utils.truncate("hello world", 5) == "he..."

    def test_truncate_zero_length(self):
        """Zero length should return empty string."""
        assert text_utils.truncate("text", 0) == ""

    def test_truncate_empty_string(self):
        """Empty string should remain empty."""
        assert text_utils.truncate("", 10) == ""

    def test_truncate_single_character(self):
        """Single character truncation."""
        result = text_utils.truncate("hello", 1)
        assert len(result) <= 1 + 3

    def test_truncate_very_long_text(self):
        """Should handle very long text."""
        long_text = "x" * 10000
        result = text_utils.truncate(long_text, 50)
        assert len(result) <= 50

    def test_truncate_preserves_start(self):
        """Truncation should start from beginning and add ellipsis."""
        result = text_utils.truncate("Important information", 10)
        # Truncate adds "..." to indicate truncation
        assert result.startswith("Im")
        assert "..." in result
        assert len(result) <= 13  # 10 chars + "..."

    def test_truncate_with_unicode(self):
        """Should handle unicode characters."""
        result = text_utils.truncate("Hello 世界", 5)
        assert len(result) <= 5


class TestHighlightMatch:
    """Tests for highlighting matched text."""

    def test_highlight_simple_match(self):
        """Should highlight matching text."""
        result = text_utils.highlight_match("Hello World", "world")
        assert "[World]" in result
        assert "Hello" in result

    def test_highlight_case_insensitive(self):
        """Highlight should be case-insensitive."""
        result = text_utils.highlight_match("Hello WORLD", "world")
        assert "[WORLD]" in result

    def test_highlight_no_match(self):
        """Text without match should be unchanged."""
        result = text_utils.highlight_match("Hello", "xyz")
        assert result == "Hello"
        assert "[" not in result

    def test_highlight_partial_match(self):
        """Should highlight partial word matches."""
        result = text_utils.highlight_match("wonderful", "on")
        assert "[on]" in result

    def test_highlight_multiple_occurrences(self):
        """Should highlight the first occurrence."""
        result = text_utils.highlight_match("aaabbbaa", "aa")
        # Highlights first occurrence only
        assert "[aa]" in result
        assert result.startswith("[aa]")

    def test_highlight_empty_query(self):
        """Empty query should return text unchanged."""
        result = text_utils.highlight_match("Hello", "")
        assert result == "Hello"


class TestNormalizeWhitespace:
    """Tests for whitespace normalization."""

    def test_normalize_leading_trailing(self):
        """Should remove leading/trailing whitespace."""
        result = text_utils.normalize_whitespace("  hello  ")
        assert result == "hello"

    def test_normalize_multiple_spaces(self):
        """Should collapse multiple spaces to single."""
        result = text_utils.normalize_whitespace("a   b   c")
        assert result == "a b c"

    def test_normalize_tabs_and_newlines(self):
        """Should handle tabs and newlines."""
        result = text_utils.normalize_whitespace("a\tb\nc")
        assert result == "a b c"

    def test_normalize_mixed_whitespace(self):
        """Should handle mixed whitespace types."""
        result = text_utils.normalize_whitespace("  a   b \n c  ")
        assert result == "a b c"

    def test_normalize_empty_string(self):
        """Empty string should remain empty."""
        result = text_utils.normalize_whitespace("")
        assert result == ""

    def test_normalize_whitespace_only(self):
        """Whitespace-only string should become empty."""
        result = text_utils.normalize_whitespace("   \t\n  ")
        assert result == ""

    def test_normalize_preserves_non_whitespace(self):
        """Should preserve actual content."""
        result = text_utils.normalize_whitespace("  hello-world_123  ")
        assert "hello-world_123" in result


class TestPluralize:
    """Tests for pluralization."""

    def test_pluralize_singular_one(self):
        """One item should use singular form."""
        assert text_utils.pluralize(1, "item") == "item"

    def test_pluralize_plural_zero(self):
        """Zero items should use plural form."""
        assert text_utils.pluralize(0, "item") == "items"

    def test_pluralize_plural_two(self):
        """Two items should use plural form."""
        assert text_utils.pluralize(2, "item") == "items"

    def test_pluralize_plural_many(self):
        """Many items should use plural form."""
        assert text_utils.pluralize(100, "item") == "items"

    def test_pluralize_custom_form(self):
        """Should use custom plural form if provided."""
        assert text_utils.pluralize(3, "child", "children") == "children"

    def test_pluralize_custom_singular(self):
        """Custom form with singular should work."""
        assert text_utils.pluralize(1, "child", "children") == "child"

    def test_pluralize_negative_number(self):
        """Negative numbers should use plural form."""
        result = text_utils.pluralize(-5, "item")
        assert result == "items"

    def test_pluralize_large_number(self):
        """Large numbers should work correctly."""
        assert text_utils.pluralize(1000000, "file", "files") == "files"

    def test_pluralize_default_plural_form(self):
        """Should add 's' if no custom form provided."""
        result = text_utils.pluralize(2, "cat")
        assert result == "cats"
