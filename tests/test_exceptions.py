import pytest

from assistant_bot.domain.exceptions import (
    PersonalAssistantError,
    ValidationError,
    StorageError,
    NotFoundError,
    ContactNotFoundError,
    NoteNotFoundError,
)


class TestExceptionHierarchy:
    """Tests for exception class hierarchy."""

    def test_personal_assistant_error_is_exception(self):
        """PersonalAssistantError should inherit from Exception."""
        assert issubclass(PersonalAssistantError, Exception)

    def test_validation_error_inherits_from_base(self):
        """ValidationError should be a subclass of PersonalAssistantError."""
        assert issubclass(ValidationError, PersonalAssistantError)

    def test_storage_error_inherits_from_base(self):
        """StorageError should be a subclass of PersonalAssistantError."""
        assert issubclass(StorageError, PersonalAssistantError)

    def test_not_found_error_inherits_from_base(self):
        """NotFoundError should be a subclass of PersonalAssistantError."""
        assert issubclass(NotFoundError, PersonalAssistantError)

    def test_contact_not_found_error_inherits_from_not_found(self):
        """ContactNotFoundError should be a subclass of NotFoundError."""
        assert issubclass(ContactNotFoundError, NotFoundError)

    def test_note_not_found_error_inherits_from_not_found(self):
        """NoteNotFoundError should be a subclass of NotFoundError."""
        assert issubclass(NoteNotFoundError, NotFoundError)

    def test_contact_not_found_error_inherits_from_base(self):
        """ContactNotFoundError should be a subclass of PersonalAssistantError."""
        assert issubclass(ContactNotFoundError, PersonalAssistantError)

    def test_note_not_found_error_inherits_from_base(self):
        """NoteNotFoundError should be a subclass of PersonalAssistantError."""
        assert issubclass(NoteNotFoundError, PersonalAssistantError)


class TestExceptionInstances:
    """Tests for creating and raising exceptions."""

    def test_personal_assistant_error_can_be_raised(self):
        """PersonalAssistantError should be raisable."""
        with pytest.raises(PersonalAssistantError):
            raise PersonalAssistantError("Test error")

    def test_validation_error_can_be_raised(self):
        """ValidationError should be raisable."""
        with pytest.raises(ValidationError):
            raise ValidationError("Invalid data")

    def test_storage_error_can_be_raised(self):
        """StorageError should be raisable."""
        with pytest.raises(StorageError):
            raise StorageError("Storage failed")

    def test_not_found_error_can_be_raised(self):
        """NotFoundError should be raisable."""
        with pytest.raises(NotFoundError):
            raise NotFoundError("Not found")

    def test_contact_not_found_error_can_be_raised(self):
        """ContactNotFoundError should be raisable."""
        with pytest.raises(ContactNotFoundError):
            raise ContactNotFoundError("Contact not found")

    def test_note_not_found_error_can_be_raised(self):
        """NoteNotFoundError should be raisable."""
        with pytest.raises(NoteNotFoundError):
            raise NoteNotFoundError("Note not found")

    def test_exception_message_preserved(self):
        """Exception message should be preserved."""
        msg = "Something went wrong"
        with pytest.raises(PersonalAssistantError) as exc_info:
            raise PersonalAssistantError(msg)
        assert str(exc_info.value) == msg

    def test_specific_exception_caught_as_base(self):
        """Specific exceptions should be catchable as base exception."""
        with pytest.raises(PersonalAssistantError):
            raise ValidationError("Test")

    def test_contact_not_found_caught_as_not_found(self):
        """ContactNotFoundError should be catchable as NotFoundError."""
        with pytest.raises(NotFoundError):
            raise ContactNotFoundError("Contact missing")

    def test_note_not_found_caught_as_not_found(self):
        """NoteNotFoundError should be catchable as NotFoundError."""
        with pytest.raises(NotFoundError):
            raise NoteNotFoundError("Note missing")


class TestExceptionMessages:
    """Tests for exception message handling."""

    @pytest.mark.parametrize(
        "exc_class,message",
        [
            (PersonalAssistantError, "Base error"),
            (ValidationError, "Validation failed"),
            (StorageError, "Storage failed"),
            (NotFoundError, "Not found"),
            (ContactNotFoundError, "Contact not found"),
            (NoteNotFoundError, "Note not found"),
        ],
    )
    def test_exception_message_handling(self, exc_class, message):
        """All exceptions should preserve their messages."""
        exc = exc_class(message)
        assert str(exc) == message

    def test_empty_message(self):
        """Should handle empty messages."""
        exc = PersonalAssistantError("")
        assert str(exc) == ""

    def test_exception_with_args(self):
        """Should handle exception with multiple args."""
        exc = PersonalAssistantError("Error", "Details", "More details")
        # Exception repr will show all args
        assert len(exc.args) == 3

    def test_unicode_in_message(self):
        """Should handle unicode in messages."""
        msg = "Error: 世界 🌍"
        exc = PersonalAssistantError(msg)
        assert "世界" in str(exc)
        assert "🌍" in str(exc)


class TestExceptionCatchingPatterns:
    """Tests for common exception catching patterns."""

    def test_catch_all_app_errors(self):
        """Should catch all app errors with PersonalAssistantError."""
        errors = [
            ValidationError("v"),
            StorageError("s"),
            NotFoundError("n"),
            ContactNotFoundError("c"),
            NoteNotFoundError("nn"),
        ]

        for error in errors:
            with pytest.raises(PersonalAssistantError):
                raise error

    def test_catch_validation_errors_specifically(self):
        """Should catch ValidationError but not StorageError."""
        with pytest.raises(ValidationError):
            raise ValidationError("Invalid")

        # StorageError should not be caught as ValidationError
        with pytest.raises(StorageError):
            try:
                raise StorageError("Failed")
            except ValidationError:
                pass
            except StorageError:
                raise

    def test_catch_not_found_errors(self):
        """Both NotFoundError subclasses should be caught."""
        errors = [
            ContactNotFoundError("contact"),
            NoteNotFoundError("note"),
        ]

        for error in errors:
            with pytest.raises(NotFoundError):
                raise error

    def test_distinguish_between_not_found_types(self):
        """Should distinguish between ContactNotFoundError and NoteNotFoundError."""
        with pytest.raises(ContactNotFoundError):
            raise ContactNotFoundError("contact")

        with pytest.raises(NoteNotFoundError):
            raise NoteNotFoundError("note")


class TestExceptionInheritanceChains:
    """Tests for complete inheritance chains."""

    def test_contact_not_found_inheritance_chain(self):
        """ContactNotFoundError should inherit through the chain."""
        assert isinstance(ContactNotFoundError("msg"), NotFoundError)
        assert isinstance(ContactNotFoundError("msg"), PersonalAssistantError)
        assert isinstance(ContactNotFoundError("msg"), Exception)

    def test_note_not_found_inheritance_chain(self):
        """NoteNotFoundError should inherit through the chain."""
        assert isinstance(NoteNotFoundError("msg"), NotFoundError)
        assert isinstance(NoteNotFoundError("msg"), PersonalAssistantError)
        assert isinstance(NoteNotFoundError("msg"), Exception)

    def test_validation_error_inheritance_chain(self):
        """ValidationError should inherit correctly."""
        assert isinstance(ValidationError("msg"), PersonalAssistantError)
        assert isinstance(ValidationError("msg"), Exception)

    def test_storage_error_inheritance_chain(self):
        """StorageError should inherit correctly."""
        assert isinstance(StorageError("msg"), PersonalAssistantError)
        assert isinstance(StorageError("msg"), Exception)
