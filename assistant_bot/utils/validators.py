"""Validation utilities for contacts, notes, and tags."""

from __future__ import annotations

import re
from datetime import date, datetime

import phonenumbers
from email_validator import EmailNotValidError, validate_email as ev_validate_email
from phonenumbers import NumberParseException

from assistant_bot.domain.exceptions import ValidationError


DEFAULT_PHONE_REGION = "IE"

MIN_NAME_LENGTH = 2
MAX_NAME_LENGTH = 100

MIN_ADDRESS_LENGTH = 3
MAX_ADDRESS_LENGTH = 500

MIN_TAG_LENGTH = 2
MAX_TAG_LENGTH = 50

MIN_NOTE_CONTENT_LENGTH = 2
MAX_NOTE_CONTENT_LENGTH = 10000

MIN_PHONE_DIGITS = 7
MAX_EMAIL_LENGTH = 254

POPULAR_EMAIL_DOMAINS = {
    "gmail.com",
    "outlook.com",
    "hotmail.com",
    "yahoo.com",
    "icloud.com",
}

BLOCKED_EMAIL_DOMAINS = {
    "example.com",
    "test.com",
    "ex.com",
    "example.org",
    "example.net",
    "invalid",
    "localhost",
    "mailinator.com",
    "tempmail.com",
    "fakeinbox.com",
    "trashmail.com",
    "yopmail.com",
}

BLOCKED_EMAIL_LOCAL_PARTS = {
    "test",
    "example",
    "demo",
    "sample",
    "fake",
    "mail",
    "admin",
    "user",
}

SUSPICIOUS_PHONE_PATTERNS = (
    re.compile(r"^(\d)\1{6,}$"),
    re.compile(r"^(0123456789|1234567890|9876543210)+$"),
)

BIRTHDAY_PATTERN = re.compile(r"\d{4}-\d{2}-\d{2}")
TAG_PATTERN = re.compile(r"[a-z0-9_-]+")


def _normalize_spaces(value: str) -> str:
    """Collapse repeated whitespace into single spaces."""
    return " ".join(value.strip().split())


def _require_non_empty_string(value: str, field_name: str) -> str:
    """Return a normalized string or raise if the value is empty or invalid."""
    if not isinstance(value, str):
        raise ValidationError(f"{field_name} must be a string")

    cleaned = _normalize_spaces(value)
    if not cleaned:
        raise ValidationError(f"{field_name} cannot be empty")

    return cleaned


def _contains_letters_or_digits(value: str) -> bool:
    """Return True if the value contains at least one alphanumeric character."""
    return any(char.isalnum() for char in value)


def _validate_length(
    value: str,
    *,
    field_name: str,
    minimum: int,
    maximum: int,
) -> None:
    """Validate that a string length is within the allowed inclusive range."""
    if len(value) < minimum:
        raise ValidationError(f"{field_name} must be at least {minimum} characters long")

    if len(value) > maximum:
        raise ValidationError(f"{field_name} cannot exceed {maximum} characters")


def validate_name(name: str) -> str:
    """Validate and normalize a contact name."""
    cleaned = _require_non_empty_string(name, "Name")
    _validate_length(
        cleaned,
        field_name="Name",
        minimum=MIN_NAME_LENGTH,
        maximum=MAX_NAME_LENGTH,
    )

    if not _contains_letters_or_digits(cleaned):
        raise ValidationError("Name must contain letters or numbers")

    return cleaned


def validate_email(email: str) -> str:
    """Validate and normalize an email address."""
    cleaned = _require_non_empty_string(email, "Email").lower()

    try:
        result = ev_validate_email(
            cleaned,
            check_deliverability=True,
        )
    except EmailNotValidError as error:
        raise ValidationError(str(error)) from error

    normalized_email = result.normalized
    local_part, domain = normalized_email.rsplit("@", 1)
    local_part = local_part.lower()
    domain = domain.lower()

    if domain in BLOCKED_EMAIL_DOMAINS:
        raise ValidationError(f"Email domain is not allowed: {domain}")

    if local_part in BLOCKED_EMAIL_LOCAL_PARTS and domain in POPULAR_EMAIL_DOMAINS:
        raise ValidationError("Email address looks like a placeholder or test address")

    if "." not in domain:
        raise ValidationError("Email domain must contain a valid top-level domain")

    if len(normalized_email) > MAX_EMAIL_LENGTH:
        raise ValidationError(f"Email cannot exceed {MAX_EMAIL_LENGTH} characters")

    return normalized_email


def validate_phone(phone: str, default_region: str = DEFAULT_PHONE_REGION) -> str:
    """Validate and normalize a phone number to E.164 format."""
    cleaned = _require_non_empty_string(phone, "Phone")
    compact = re.sub(r"\s+", " ", cleaned)

    digits_only = re.sub(r"\D", "", compact)
    if len(digits_only) < MIN_PHONE_DIGITS:
        raise ValidationError("Phone number is too short")

    for pattern in SUSPICIOUS_PHONE_PATTERNS:
        if pattern.fullmatch(digits_only):
            raise ValidationError("Phone number looks invalid")

    try:
        parsed_number = phonenumbers.parse(compact, default_region)
    except NumberParseException as error:
        raise ValidationError(f"Invalid phone number: {cleaned}") from error

    if not phonenumbers.is_possible_number(parsed_number):
        raise ValidationError("Phone number is not possible")

    if not phonenumbers.is_valid_number(parsed_number):
        raise ValidationError("Phone number is not valid")

    return phonenumbers.format_number(
        parsed_number,
        phonenumbers.PhoneNumberFormat.E164,
    )


def validate_address(address: str) -> str:
    """Validate and normalize a contact address."""
    cleaned = _require_non_empty_string(address, "Address")
    _validate_length(
        cleaned,
        field_name="Address",
        minimum=MIN_ADDRESS_LENGTH,
        maximum=MAX_ADDRESS_LENGTH,
    )

    if not _contains_letters_or_digits(cleaned):
        raise ValidationError("Address must contain letters or numbers")

    return cleaned


def validate_birthday(birthday: str) -> str:
    """Validate birthday format as YYYY-MM-DD."""
    cleaned = _require_non_empty_string(birthday, "Birthday")

    if not BIRTHDAY_PATTERN.fullmatch(cleaned):
        raise ValidationError("Birthday must be in format YYYY-MM-DD")

    try:
        birth_date = datetime.strptime(cleaned, "%Y-%m-%d").date()
    except ValueError as error:
        raise ValidationError("Invalid date") from error

    if birth_date > date.today():
        raise ValidationError("Birthday cannot be in the future")

    return cleaned


def normalize_tag(tag: str) -> str:
    """Normalize a tag to lowercase trimmed form."""
    if not isinstance(tag, str):
        return ""
    return _normalize_spaces(tag).lower()


def validate_tag(tag: str) -> str:
    """Validate and normalize a tag."""
    cleaned = normalize_tag(tag)

    if not cleaned:
        raise ValidationError("Tag cannot be empty")

    _validate_length(
        cleaned,
        field_name="Tag",
        minimum=MIN_TAG_LENGTH,
        maximum=MAX_TAG_LENGTH,
    )

    if not TAG_PATTERN.fullmatch(cleaned):
        raise ValidationError(
            "Tag can only contain lowercase letters, numbers, hyphens, and underscores"
        )

    return cleaned


def validate_note_content(content: str) -> str:
    """Validate and normalize note content."""
    cleaned = _require_non_empty_string(content, "Note content")
    _validate_length(
        cleaned,
        field_name="Note content",
        minimum=MIN_NOTE_CONTENT_LENGTH,
        maximum=MAX_NOTE_CONTENT_LENGTH,
    )
    return cleaned