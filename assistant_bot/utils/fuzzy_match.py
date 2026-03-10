"""Fuzzy matching utilities for command suggestions."""

from __future__ import annotations

from difflib import SequenceMatcher


def _normalize(value: str) -> str:
    """Normalize text for fuzzy matching."""
    return value.strip().lower()


def similarity(a: str, b: str) -> float:
    """Return a similarity score between two strings in the range [0.0, 1.0]."""
    a_norm = _normalize(a)
    b_norm = _normalize(b)

    if not a_norm or not b_norm:
        return 0.0

    if a_norm == b_norm:
        return 1.0

    base_score = SequenceMatcher(None, a_norm, b_norm).ratio()

    # Strong boost for prefix matches such as:
    # add-con -> add-contact
    if b_norm.startswith(a_norm):
        return min(1.0, base_score + 0.25)

    # Boost when the input matches the beginning of any token split by '-'
    # Example: "contact" vs "add-contact"
    b_parts = b_norm.split("-")
    if any(part.startswith(a_norm) for part in b_parts):
        return min(1.0, base_score + 0.15)

    # Small boost when input is contained in the candidate
    if a_norm in b_norm:
        return min(1.0, base_score + 0.10)

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

    unique_candidates = list(dict.fromkeys(candidates))
    scored_candidates = [
        (candidate, similarity(normalized_input, candidate))
        for candidate in unique_candidates
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

    unique_candidates = list(dict.fromkeys(candidates))
    matches: list[tuple[str, float]] = []

    for candidate in unique_candidates:
        score = similarity(normalized_input, candidate)
        if score >= threshold:
            matches.append((candidate, score))

    matches.sort(key=lambda item: (-item[1], item[0]))
    return [candidate for candidate, _ in matches]