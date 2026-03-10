"""Text processing and formatting utilities."""

from __future__ import annotations

import re


def truncate(text: str, max_length: int, suffix: str = "...") -> str:
    """Truncate text to the requested maximum length."""
    if max_length <= 0:
        return ""

    if len(text) <= max_length:
        return text

    if len(suffix) >= max_length:
        return text[:max_length]

    available = max_length - len(suffix)
    return text[:available] + suffix


def highlight_match(text: str, query: str) -> str:
    """Return text with the first query match wrapped in square brackets."""
    if not text or not query:
        return text

    lower_text = text.lower()
    lower_query = query.lower()
    start_index = lower_text.find(lower_query)

    if start_index == -1:
        return text

    end_index = start_index + len(query)
    before = text[:start_index]
    match = text[start_index:end_index]
    after = text[end_index:]

    return f"{before}[{match}]{after}"


def normalize_whitespace(text: str) -> str:
    """Normalize whitespace by collapsing runs of whitespace into single spaces."""
    return re.sub(r"\s+", " ", text).strip()


def pluralize(count: int, singular: str, plural: str | None = None) -> str:
    """Return the singular or plural word form for the provided count."""
    if count == 1:
        return singular
    return plural if plural is not None else f"{singular}s"