"""Utilities package exports."""

from assistant_bot.utils.datetime_utils import (
    days_until_birthday,
    format_birthday,
    format_birthday_with_days,
    get_birthdays_in_n_days,
)
from assistant_bot.utils.fuzzy_match import (
    find_all_similar,
    find_closest_match,
    similarity,
)
from assistant_bot.utils.text_utils import (
    highlight_match,
    normalize_whitespace,
    pluralize,
    truncate,
)
from assistant_bot.utils.validators import (
    normalize_tag,
    validate_address,
    validate_birthday,
    validate_email,
    validate_name,
    validate_note_content,
    validate_phone,
    validate_tag,
)

__all__ = [
    "days_until_birthday",
    "find_all_similar",
    "find_closest_match",
    "format_birthday",
    "format_birthday_with_days",
    "get_birthdays_in_n_days",
    "highlight_match",
    "normalize_tag",
    "normalize_whitespace",
    "pluralize",
    "similarity",
    "truncate",
    "validate_address",
    "validate_birthday",
    "validate_email",
    "validate_name",
    "validate_note_content",
    "validate_phone",
    "validate_tag",
]