"""
Custom Exception Hierarchy
===========================
All platform-specific exceptions inherit from ``AppBaseException``.

Design
------
* A typed exception hierarchy lets global handlers pattern-match on type
  rather than on magic strings or HTTP codes.
* Every exception carries a machine-readable ``error_code`` so API clients
  can switch on it without parsing the human-readable ``message``.
* ``detail`` accepts any serialisable value for rich diagnostic context.
* HTTP status codes live on the exception so the global handler needs no
  lookup table.

Adding exceptions for new modules
-----------------------------------
Define the new exception class here and inherit from ``AppBaseException``.
The global handler in ``exceptions/handlers.py`` picks it up automatically.
"""

from __future__ import annotations

from typing import Any, Optional


class AppBaseException(Exception):
    """
    Root of the platform exception hierarchy.

    All custom exceptions must inherit from this class so the global handler
    catches them with a single ``except`` clause.

    Attributes
    ----------
    message:
        Human-readable description shown to API consumers.
    error_code:
        Machine-readable identifier clients switch on (e.g. ``"RESOURCE_NOT_FOUND"``).
    detail:
        Optional supplementary information — string, dict, or list.
    http_status_code:
        HTTP status code returned to the caller.
    """

    http_status_code: int = 500
    error_code: str = "INTERNAL_SERVER_ERROR"

    def __init__(
        self,
        message: str,
        detail: Optional[Any] = None,
        error_code: Optional[str] = None,
    ) -> None:
        self.message = message
        self.detail = detail
        if error_code is not None:
            self.error_code = error_code
        super().__init__(message)

    def __repr__(self) -> str:
        return (
            f"{self.__class__.__name__}("
            f"error_code={self.error_code!r}, "
            f"message={self.message!r})"
        )


# ---------------------------------------------------------------------------
# Infrastructure exceptions
# ---------------------------------------------------------------------------

class StorageError(AppBaseException):
    """Raised when the storage layer fails to read or write a record."""

    http_status_code = 500
    error_code = "STORAGE_ERROR"


class ConfigurationError(AppBaseException):
    """Raised when required configuration is missing or invalid at startup."""

    http_status_code = 500
    error_code = "CONFIGURATION_ERROR"


# ---------------------------------------------------------------------------
# Domain exceptions
# ---------------------------------------------------------------------------

class ResourceNotFoundError(AppBaseException):
    """Raised when a requested resource does not exist."""

    http_status_code = 404
    error_code = "RESOURCE_NOT_FOUND"


class ValidationError(AppBaseException):
    """Raised when incoming data fails domain-level validation."""

    http_status_code = 422
    error_code = "VALIDATION_ERROR"


class UnauthorizedError(AppBaseException):
    """Raised when a request lacks valid authentication credentials."""

    http_status_code = 401
    error_code = "UNAUTHORIZED"


class ForbiddenError(AppBaseException):
    """Raised when credentials lack sufficient permissions."""

    http_status_code = 403
    error_code = "FORBIDDEN"


class ServiceUnavailableError(AppBaseException):
    """Raised when a downstream service (LLM, AWS, etc.) is unavailable."""

    http_status_code = 503
    error_code = "SERVICE_UNAVAILABLE"
