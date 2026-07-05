"""
Log Deduplicator
================
Stateless within-batch deduplication of NormalizedLog objects.

Deduplication is based on the stable identity fields of a log:
  service + component + log_level + message

Timestamps and metadata are intentionally excluded from the key so that
burst-repeated log entries (same message, milliseconds apart) are detected
and discarded.

The first occurrence within the batch is always preserved.
"""

from __future__ import annotations

import logging

from app.engines.log_processing.normalizer import compute_dedup_key
from app.schemas.domain import NormalizedLog

logger = logging.getLogger("ai_analysis_engine.engines.log_processing.deduplicator")


def deduplicate(logs: list[NormalizedLog]) -> list[NormalizedLog]:
    """
    Remove duplicate log entries from a batch.

    The first occurrence of each unique (service, component, log_level, message)
    combination is kept. All subsequent duplicates are silently discarded and
    counted in the summary log.

    Parameters
    ----------
    logs:
        A list of NormalizedLog objects produced by the normalization step.

    Returns
    -------
    list[NormalizedLog]
        A deduplicated list that preserves the original insertion order.
    """
    if not logs:
        return []

    seen: set[str] = set()
    unique: list[NormalizedLog] = []

    for log in logs:
        key = compute_dedup_key(
            log.service, log.component, log.log_level, log.message
        )
        if key in seen:
            logger.debug(
                "Duplicate discarded | log_id=%s | service=%s | component=%s",
                log.log_id,
                log.service,
                log.component,
            )
        else:
            seen.add(key)
            unique.append(log)

    discarded = len(logs) - len(unique)
    if discarded:
        logger.info(
            "Deduplication complete | input=%d | unique=%d | discarded=%d",
            len(logs),
            len(unique),
            discarded,
        )

    return unique
