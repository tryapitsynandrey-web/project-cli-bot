"""Custom exceptions for the personal assistant domain."""


class PersonalAssistantError(Exception):
    """Base exception for all application-specific errors."""


class ValidationError(PersonalAssistantError):
    """Raised when validation of user or stored data fails."""


class StorageError(PersonalAssistantError):
    """Raised when loading or saving data fails."""


class NotFoundError(PersonalAssistantError):
    """Raised when a requested entity cannot be found."""


class ContactNotFoundError(NotFoundError):
    """Raised when a contact cannot be found."""


class NoteNotFoundError(NotFoundError):
    """Raised when a note cannot be found."""