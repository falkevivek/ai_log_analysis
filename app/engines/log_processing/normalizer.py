"""
Log Normalizer
==============
Pure, stateless functions for normalizing individual fields of a raw log entry.

Every function in this module has exactly one responsibility.
They are imported and composed by the LogProcessingEngine.

No business logic. No AI reasoning. No side effects.
Only data transformation.
"""

from __future__ import annotations

import hashlib
import re
import uuid
from datetime import datetime, timezone
from typing import Any, Optional


# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

_KNOWN_LOG_LEVELS: frozenset[str] = frozenset({
    "DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL",
})

# Aliases that map non-standard levels to canonical ones.
_LOG_LEVEL_ALIASES: dict[str, str] = {
    "WARN": "WARNING",
    "FATAL": "CRITICAL",
    "SEVERE": "CRITICAL",
    "TRACE": "DEBUG",
    "VERBOSE": "DEBUG",
}

# Ordered list of (regex_pattern, placeholder) tuples used for template extraction.
# Order matters: more specific patterns must come before more general ones.
_TEMPLATE_PATTERNS: list[tuple[str, str]] = [
    # ISO timestamps inside the message body
    (
        r"\d{4}-\d{2}-\d{2}[T ]\d{2}:\d{2}:\d{2}(?:\.\d+)?(?:Z|[+-]\d{2}:\d{2})?",
        "<TIMESTAMP>",
    ),
    # IPv4 addresses
    (
        r"\b(?:\d{1,3}\.){3}\d{1,3}\b",
        "<IP>",
    ),
    # UUIDs
    (
        r"\b[0-9a-fA-F]{8}-(?:[0-9a-fA-F]{4}-){3}[0-9a-fA-F]{12}\b",
        "<UUID>",
    ),
    # Double-quoted string values
    (
        r'"[^"]{1,200}"',
        "<STRING>",
    ),
    # Single-quoted string values
    (
        r"'[^']{1,200}'",
        "<STRING>",
    ),
    # Standalone large integers (IDs, error codes, ports, durations)
    (
        r"\b\d{4,}\b",
        "<NUMBER>",
    ),
]

# Common timestamp format strings to try when ISO parsing fails.
_TIMESTAMP_FORMATS: tuple[str, ...] = (
    "%Y-%m-%d %H:%M:%S",
    "%Y-%m-%dT%H:%M:%S",
    "%d/%b/%Y:%H:%M:%S %z",
    "%Y/%m/%d %H:%M:%S",
    "%d-%m-%Y %H:%M:%S",
    "%m/%d/%Y %H:%M:%S",
)


# ---------------------------------------------------------------------------
# Field normalizers
# ---------------------------------------------------------------------------

def normalize_log_id(log_id: Optional[str]) -> str:
    """
    Return the log_id unchanged if it is a non-empty string.
    Generate a new UUID4 string if the log_id is absent or blank.

    This function never raises — a missing ID is auto-generated.
    """
    if log_id and str(log_id).strip():
        return str(log_id).strip()
    return str(uuid.uuid4())


def normalize_timestamp(timestamp: Any) -> datetime:
    """
    Convert any timestamp representation to a timezone-aware UTC datetime.

    Accepts datetime objects, Unix epoch integers/floats, and ISO 8601 strings
    in a variety of common formats.

    Raises
    ------
    ValueError
        If the timestamp cannot be parsed into a datetime object.
    """
    if isinstance(timestamp, datetime):
        if timestamp.tzinfo is None:
            # Treat naive datetimes as UTC (most common case for log engines).
            return timestamp.replace(tzinfo=timezone.utc)
        return timestamp.astimezone(timezone.utc)

    if isinstance(timestamp, (int, float)):
        return datetime.fromtimestamp(float(timestamp), tz=timezone.utc)

    if isinstance(timestamp, str):
        ts = timestamp.strip()
        # Handle the "Z" suffix that Python < 3.11 does not support natively.
        ts_iso = ts.replace("Z", "+00:00")
        try:
            dt = datetime.fromisoformat(ts_iso)
            if dt.tzinfo is None:
                dt = dt.replace(tzinfo=timezone.utc)
            return dt.astimezone(timezone.utc)
        except ValueError:
            pass

        # Try common format strings as fallback.
        for fmt in _TIMESTAMP_FORMATS:
            try:
                dt = datetime.strptime(ts, fmt)
                if dt.tzinfo is None:
                    dt = dt.replace(tzinfo=timezone.utc)
                return dt.astimezone(timezone.utc)
            except ValueError:
                continue

    raise ValueError(
        f"Cannot parse timestamp {timestamp!r}. "
        "Expected a datetime object, Unix epoch number, or ISO 8601 string."
    )


def normalize_log_level(log_level: Any) -> str:
    """
    Normalize a log level to a canonical uppercase string.

    Handles aliases (WARN → WARNING, FATAL → CRITICAL).
    Returns "UNKNOWN" for unrecognized levels rather than raising,
    preserving the log entry for downstream inspection.
    """
    if not log_level:
        return "UNKNOWN"
    normalized = str(log_level).strip().upper()
    # Resolve aliases first.
    normalized = _LOG_LEVEL_ALIASES.get(normalized, normalized)
    return normalized if normalized in _KNOWN_LOG_LEVELS else "UNKNOWN"


def normalize_service(service: Any) -> str:
    """
    Normalize a service name to lowercase with whitespace stripped.
    Returns "unknown-service" for missing or blank values.
    """
    if not service or not str(service).strip():
        return "unknown-service"
    return str(service).strip().lower()


def normalize_component(component: Any) -> str:
    """
    Normalize a component name to lowercase with whitespace stripped.
    Returns "unknown-component" for missing or blank values.
    """
    if not component or not str(component).strip():
        return "unknown-component"
    return str(component).strip().lower()


def normalize_message(message: Any) -> str:
    """
    Strip surrounding whitespace from the log message.

    Raises
    ------
    ValueError
        If the message is None, empty, or blank after stripping.
    """
    if message is None:
        raise ValueError("Log message is None.")
    cleaned = str(message).strip()
    if not cleaned:
        raise ValueError("Log message is empty or contains only whitespace.")
    return cleaned


# ---------------------------------------------------------------------------
# Template extraction
# ---------------------------------------------------------------------------

def extract_template(message: str) -> tuple[Optional[str], dict[str, Any]]:
    """
    Apply regex substitutions to extract a log template and its variable parameters.

    Substitutes recognized variable parts (IPs, UUIDs, timestamps, numbers,
    quoted strings) with typed placeholders. Returns the templatized string
    and a dictionary of extracted values.

    If no substitutions are possible, returns (None, {}).

    Parameters
    ----------
    message:
        A normalized, non-empty log message string.

    Returns
    -------
    tuple[Optional[str], dict[str, Any]]
        A (template, parameters) pair. ``template`` is None when no
        substitutions were made.
    """
    template = message
    parameters: dict[str, Any] = {}

    for pattern, placeholder in _TEMPLATE_PATTERNS:
        matches = re.findall(pattern, template)
        if matches:
            key = placeholder.strip("<>").lower()
            # Accumulate multiple matches under the same placeholder key.
            existing = parameters.get(key)
            if existing is None:
                parameters[key] = matches[0] if len(matches) == 1 else matches
            elif isinstance(existing, list):
                parameters[key] = existing + matches
            else:
                parameters[key] = [existing] + matches
            template = re.sub(pattern, placeholder, template)

    if template == message:
        return None, {}

    return template, parameters


# ---------------------------------------------------------------------------
# Deduplication key
# ---------------------------------------------------------------------------

def compute_dedup_key(
    service: str,
    component: str,
    log_level: str,
    message: str,
) -> str:
    """
    Compute a SHA-256 deduplication hash from the stable identity fields of a log.

    Timestamps and metadata are intentionally excluded so that the same message
    emitted multiple times within a short window is detected as a duplicate.
    """
    content = f"{service}|{component}|{log_level}|{message}"
    return hashlib.sha256(content.encode("utf-8")).hexdigest()
