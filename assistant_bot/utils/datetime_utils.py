"""Utilities for date and time operations."""

from __future__ import annotations

from datetime import date, datetime


def _parse_date(value: str | None) -> date | None:
    """Parse a YYYY-MM-DD string into a date object."""
    if not value:
        return None

    try:
        return datetime.strptime(value, "%Y-%m-%d").date()
    except (TypeError, ValueError):
        return None


def _safe_birthday_for_year(birth_date: date, year: int) -> date:
    """Return a birthday date for the given year, handling leap years safely."""
    try:
        return birth_date.replace(year=year)
    except ValueError:
        # Handle Feb 29 in non-leap years as Feb 28
        return date(year, 2, 28)


def days_until_birthday(birthday_str: str | None) -> int:
    """Return the number of days until the next birthday.

    Returns:
        0 if birthday is today
        positive integer if upcoming
        -1 if birthday is missing or invalid
    """
    birth_date = _parse_date(birthday_str)
    if birth_date is None:
        return -1

    today = date.today()
    next_birthday = _safe_birthday_for_year(birth_date, today.year)

    if next_birthday < today:
        next_birthday = _safe_birthday_for_year(birth_date, today.year + 1)

    return (next_birthday - today).days


def format_birthday(birthday_str: str | None) -> str:
    """Format a birthday string for display."""
    birth_date = _parse_date(birthday_str)
    if birth_date is None:
        return ""

    return birth_date.strftime("%b %d, %Y")


def format_birthday_with_days(birthday_str: str | None, days_left: int | None = None) -> str:
    """Format a birthday string together with time remaining until the next birthday."""
    formatted = format_birthday(birthday_str)
    if not formatted:
        return ""

    if days_left is None:
        days_left = days_until_birthday(birthday_str)

    if days_left < 0:
        return formatted
    if days_left == 0:
        return f"{formatted} (today)"
    if days_left == 1:
        return f"{formatted} (tomorrow)"
    return f"{formatted} ({days_left} days left)"


def get_birthdays_in_n_days(
    birthdays: dict[str, str],
    days: int,
) -> list[tuple[str, str, int]]:
    """Return birthdays occurring within the next given number of days."""
    if days < 0:
        return []

    result: list[tuple[str, str, int]] = []

    for contact_id, birthday_str in birthdays.items():
        days_left = days_until_birthday(birthday_str)
        if 0 <= days_left <= days:
            result.append((contact_id, birthday_str, days_left))

    result.sort(key=lambda item: item[2])
    return result