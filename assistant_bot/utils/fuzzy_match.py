"""Fuzzy matching utilities for command suggestions."""

from __future__ import annotations

from difflib import SequenceMatcher
from typing import Iterable

PREFIX_MATCH_BOOST = 0.25
TOKEN_PREFIX_MATCH_BOOST = 0.15
SUBSTRING_MATCH_BOOST = 0.10


def _normalize(value: str) -> str:
    """Normalize text for fuzzy matching."""
    return value.strip().lower()


def _unique_candidates(candidates: Iterable[str]) -> list[str]:
    """Return candidates with duplicates removed, preserving order."""
    return list(dict.fromkeys(candidates))


def similarity(a: str, b: str) -> float:
    """Return a similarity score between two strings in the range [0.0, 1.0]."""
    left = _normalize(a)
    right = _normalize(b)

    if not left or not right:
        return 0.0

    if left == right:
        return 1.0

    base_score = SequenceMatcher(None, left, right).ratio()

    if right.startswith(left):
        return min(1.0, base_score + PREFIX_MATCH_BOOST)

    right_parts = right.split("-")
    if any(part.startswith(left) for part in right_parts):
        return min(1.0, base_score + TOKEN_PREFIX_MATCH_BOOST)

    if left in right:
        return min(1.0, base_score + SUBSTRING_MATCH_BOOST)

    return base_score


def find_closest_match(
    user_input: str,
    candidates: list[str],
    threshold: float = 0.6,
) -> str | None:
    """Return the single closest matching candidate above the threshold."""
    normalized_input = _normalize(user_input)
    if not normalized_input or not candidates:
        return None

    scored_candidates = [
        (candidate, similarity(normalized_input, candidate))
        for candidate in _unique_candidates(candidates)
    ]
    best_match, best_score = max(scored_candidates, key=lambda item: item[1])

    if best_score >= threshold:
        return best_match

    return None


def find_all_similar(
    user_input: str,
    candidates: list[str],
    threshold: float = 0.5,
) -> list[str]:
    """Return all matching candidates sorted by similarity descending."""
    normalized_input = _normalize(user_input)
    if not normalized_input or not candidates:
        return []

    matches: list[tuple[str, float]] = []

    for candidate in _unique_candidates(candidates):
        score = similarity(normalized_input, candidate)
        if score >= threshold:
            matches.append((candidate, score))

    matches.sort(key=lambda item: (-item[1], item[0]))
    return [candidate for candidate, _ in matches]