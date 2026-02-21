"""Custom exception classes."""


class AppException(Exception):
    """Base application exception."""

    pass


class NotFoundError(AppException):
    """Resource not found exception."""

    pass


class ValidationError(AppException):
    """Validation error exception."""

    pass


class ConflictError(AppException):
    """Resource conflict exception."""

    pass
