from __future__ import annotations

import sys
import types
from types import SimpleNamespace
from typing import Any

import pytest


def _install_phonenumbers_stub() -> None:
    """Install a lightweight phonenumbers stub into sys.modules for tests."""
    if "phonenumbers" in sys.modules:
        return

    ph: Any = types.ModuleType("phonenumbers")

    class NumberParseException(Exception):
        """Stub parse exception."""

    class PhoneNumberFormat:
        """Stub phone number format enum."""
        E164 = 1

    def _dummy_parse(number: str, region: str | None = None) -> object:
        class _Number:
            pass

        return _Number()

    def _dummy_is_possible_number(number_obj: object) -> bool:
        return True

    def _dummy_is_valid_number(number_obj: object) -> bool:
        return True

    def _dummy_format_number(number_obj: object, fmt: int) -> str:
        return "+10000000000"

    ph.parse = _dummy_parse
    ph.NumberParseException = NumberParseException
    ph.is_possible_number = _dummy_is_possible_number
    ph.is_valid_number = _dummy_is_valid_number
    ph.PhoneNumberFormat = PhoneNumberFormat
    ph.format_number = _dummy_format_number

    sys.modules["phonenumbers"] = ph


def _install_email_validator_stub() -> None:
    """Install a lightweight email_validator stub into sys.modules for tests."""
    if "email_validator" in sys.modules:
        return

    ev: Any = types.ModuleType("email_validator")

    class EmailNotValidError(Exception):
        """Stub email validation exception."""

    def _dummy_validate_email(
        value: str,
        check_deliverability: bool = True,
    ) -> object:
        return SimpleNamespace(normalized=value)

    ev.EmailNotValidError = EmailNotValidError
    ev.validate_email = _dummy_validate_email

    sys.modules["email_validator"] = ev


_install_phonenumbers_stub()
_install_email_validator_stub()


@pytest.fixture(autouse=True)
def patch_external_validators(monkeypatch: pytest.MonkeyPatch):
    """Patch external validators to deterministic fakes for tests."""

    def _fake_ev_validate_email(
        value: str,
        check_deliverability: bool = True,
    ) -> SimpleNamespace:
        return SimpleNamespace(normalized=value)

    monkeypatch.setattr(
        "assistant_bot.utils.validators.ev_validate_email",
        _fake_ev_validate_email,
        raising=False,
    )

    class _FakeNumber:
        pass

    def _fake_parse(number: str, region: str | None = None) -> _FakeNumber:
        return _FakeNumber()

    def _fake_is_possible_number(obj: object) -> bool:
        return True

    def _fake_is_valid_number(obj: object) -> bool:
        return True

    def _fake_format_number(obj: object, fmt: object) -> str:
        return "+10000000000"

    monkeypatch.setattr(
        "assistant_bot.utils.validators.phonenumbers.parse",
        _fake_parse,
        raising=False,
    )
    monkeypatch.setattr(
        "assistant_bot.utils.validators.phonenumbers.is_possible_number",
        _fake_is_possible_number,
        raising=False,
    )
    monkeypatch.setattr(
        "assistant_bot.utils.validators.phonenumbers.is_valid_number",
        _fake_is_valid_number,
        raising=False,
    )
    monkeypatch.setattr(
        "assistant_bot.utils.validators.phonenumbers.format_number",
        _fake_format_number,
        raising=False,
    )

    yield


@pytest.fixture
def fake_contact_repository():
    from tests.fakes import FakeContactRepository

    return FakeContactRepository()


@pytest.fixture
def fake_note_repository():
    from tests.fakes import FakeNoteRepository

    return FakeNoteRepository()


@pytest.fixture
def sample_contact_payload():
    from tests.builders import build_contact_payload

    return build_contact_payload()


@pytest.fixture
def sample_note_payload():
    from tests.builders import build_note_payload

    return build_note_payload()


@pytest.fixture
def sample_contact(fake_contact_repository, sample_contact_payload):
    fake_contact_repository.seed_contacts([sample_contact_payload])

    from assistant_bot.domain.contacts import Contact

    return Contact.from_dict(sample_contact_payload)


@pytest.fixture
def sample_note(fake_note_repository, sample_note_payload):
    fake_note_repository.seed_notes([sample_note_payload])

    from assistant_bot.domain.notes import Note

    return Note.from_dict(sample_note_payload)


@pytest.fixture
def contact_service(fake_contact_repository):
    from assistant_bot.services.contact_service import ContactService

    return ContactService(fake_contact_repository)


@pytest.fixture
def note_service(fake_note_repository):
    from assistant_bot.services.note_service import NoteService

    return NoteService(fake_note_repository)


@pytest.fixture
def tmp_data_dir(monkeypatch: pytest.MonkeyPatch, tmp_path):
    """Force JSONStorage to use a temporary data directory during tests."""
    monkeypatch.setattr(
        "assistant_bot.storage.paths.get_data_dir",
        lambda: tmp_path,
    )
    return tmp_path