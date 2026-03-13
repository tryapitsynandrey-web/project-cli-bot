"""Utilities for date and time operations."""

from __future__ import annotations

from datetime import date, datetime

DATE_INPUT_FORMAT = "%Y-%m-%d"
BIRTHDAY_DISPLAY_FORMAT = "%b %d, %Y"
INVALID_BIRTHDAY_DAYS = -1


def _parse_date(value: str | None) -> date | None:
    """Parse a YYYY-MM-DD string into a date object."""
    if not value:
        return None

    try:
        return datetime.strptime(value, DATE_INPUT_FORMAT).date()
    except (TypeError, ValueError):
        return None


def _safe_birthday_for_year(birth_date: date, year: int) -> date:
    """Return a birthday date for the given year, handling leap years safely."""
    try:
        return birth_date.replace(year=year)
    except ValueError:
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
        return INVALID_BIRTHDAY_DAYS

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

    return birth_date.strftime(BIRTHDAY_DISPLAY_FORMAT)


def format_birthday_with_days(
    birthday_str: str | None,
    days_left: int | None = None,
) -> str:
    """Format a birthday string together with time remaining until the next birthday."""
    formatted = format_birthday(birthday_str)
    if not formatted:
        return ""

    remaining_days = (
        days_until_birthday(birthday_str)
        if days_left is None
        else days_left
    )

    if remaining_days < 0:
        return formatted
    if remaining_days == 0:
        return f"{formatted} (today)"
    if remaining_days == 1:
        return f"{formatted} (tomorrow)"
    return f"{formatted} ({remaining_days} days left)"


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