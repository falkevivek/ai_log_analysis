"""
Log Validator
=============
Validates that a raw log dictionary satisfies the minimum field requirements
before normalization is attempted.

Design note
-----------
Validation is intentionally separated from normalization so that the
LogProcessingEngine can enforce the contract boundary clearly:
  1. Validate (reject or flag) → 2. Normalize (transform)

Only hard-required fields raise ValidationError.
Optional or defaultable fields are allowed to be absent.
"""

from __future__ import annotations

from typing import Any

from app.exceptions.custom_exceptions import ValidationError

# Fields whose absence or emptiness must immediately abort processing.
# Timestamps and log_id are handled separately (timestamp can be repaired;
# log_id can be auto-generated).
_HARD_REQUIRED_FIELDS: tuple[str, ...] = ("message",)


def validate_raw_log_fields(data: dict[str, Any]) -> None:
    """
    Validate that a raw log dictionary contains all hard-required fields.

    Parameters
    ----------
    data:
        Dictionary representation of a RawLog object.

    Raises
    ------
    ValidationError
        If any hard-required field is missing or empty.
    """
    for field in _HARD_REQUIRED_FIELDS:
        value = data.get(field)

        if value is None:
            raise ValidationError(
                message=f"Required field '{field}' is missing from the log input.",
                detail={
                    "field": field,
                    "log_id": data.get("log_id"),
                    "service": data.get("service"),
                },
            )

        if isinstance(value, str) and not value.strip():
            raise ValidationError(
                message=f"Required field '{field}' is blank or contains only whitespace.",
                detail={
                    "field": field,
                    "log_id": data.get("log_id"),
                    "service": data.get("service"),
                },
            )
