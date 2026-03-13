"""Text processing and formatting utilities."""

from __future__ import annotations

import re

WHITESPACE_PATTERN = re.compile(r"\s+")


def truncate(text: str, max_length: int, suffix: str = "...") -> str:
    """Truncate text to the requested maximum length."""
    if max_length <= 0:
        return ""

    if len(text) <= max_length:
        return text

    if not suffix:
        return text[:max_length]

    if len(suffix) >= max_length:
        return text[:max_length]

    available_length = max_length - len(suffix)
    return text[:available_length] + suffix


def highlight_match(text: str, query: str) -> str:
    """Return text with the first query match wrapped in square brackets."""
    if not text or not query:
        return text

    normalized_text = text.lower()
    normalized_query = query.lower()
    match_start = normalized_text.find(normalized_query)

    if match_start == -1:
        return text

    match_end = match_start + len(query)
    before = text[:match_start]
    match = text[match_start:match_end]
    after = text[match_end:]

    return f"{before}[{match}]{after}"


def normalize_whitespace(text: str) -> str:
    """Normalize whitespace by collapsing runs of whitespace into single spaces."""
    return WHITESPACE_PATTERN.sub(" ", text).strip()


def pluralize(count: int, singular: str, plural: str | None = None) -> str:
    """Return the singular or plural word form for the provided count."""
    if count == 1:
        return singular
    return plural if plural is not None else f"{singular}s"