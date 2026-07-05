"""
Log Processing Engine
======================
Stage 1 of the AI Analysis pipeline.

Transforms a RawLog domain object into a clean, standardized NormalizedLog
domain object ready for consumption by the Observation Engine.

Responsibilities
----------------
1. Validate required fields (via validator module).
2. Normalize timestamp to UTC-aware datetime (via normalizer).
3. Normalize log level to canonical uppercase string (via normalizer).
4. Normalize service and component names to lowercase (via normalizer).
5. Generate a log_id if the incoming log has none (via normalizer).
6. Extract a log template and variable parameters (via normalizer).
7. Preserve all original metadata unchanged.
8. Deduplicate within a batch (via deduplicator).

This engine does NOT
--------------------
- Classify errors or anomalies.
- Detect observations or events.
- Perform AI reasoning of any kind.
- Call external services.
- Write to storage.

Interface contract
------------------
Input  → RawLog       (from app.schemas.domain)
Output → NormalizedLog (from app.schemas.domain)

The engine exposes two public methods:
  process()        — single log transformation
  process_batch()  — batch transformation with deduplication

Both methods are synchronous. The Observation Engine (Stage 2) will call
process_batch() and receive a deduplicated list[NormalizedLog].
"""

from __future__ import annotations

import logging
from typing import Any

from app.engines.log_processing.deduplicator import deduplicate
from app.engines.log_processing.normalizer import (
    extract_template,
    normalize_component,
    normalize_log_id,
    normalize_log_level,
    normalize_message,
    normalize_service,
    normalize_timestamp,
)
from app.engines.log_processing.validator import validate_raw_log_fields
from app.exceptions.custom_exceptions import ValidationError
from app.schemas.domain import NormalizedLog, RawLog

logger = logging.getLogger("ai_analysis_engine.engines.log_processing.engine")


class LogProcessingEngine:
    """
    Transforms RawLog objects into NormalizedLog domain objects.

    This class is intentionally stateless with respect to individual log
    processing. Batch-level deduplication state is local to each
    ``process_batch()`` call and is discarded after the call returns.

    Typical usage
    -------------
    engine = LogProcessingEngine()

    # Single log
    normalized: NormalizedLog = engine.process(raw_log)

    # Batch of logs (deduplication included)
    normalized_batch: list[NormalizedLog] = engine.process_batch(raw_logs)
    """

    # ------------------------------------------------------------------
    # Public interface
    # ------------------------------------------------------------------

    def process(self, raw_log: RawLog) -> NormalizedLog:
        """
        Transform a single RawLog into a NormalizedLog.

        Validates required fields before normalization. Raises
        ValidationError on any hard contract violation so the caller
        (or batch processor) can react appropriately.

        Parameters
        ----------
        raw_log:
            A RawLog domain object received from the ingestion layer.

        Returns
        -------
        NormalizedLog
            A fully populated, validated NormalizedLog ready for
            the Observation Engine.

        Raises
        ------
        ValidationError
            When a required field is missing, empty, or unparseable.
        """
        logger.debug(
            "Processing log | log_id=%s | service=%s | level=%s",
            raw_log.log_id,
            raw_log.service,
            raw_log.log_level,
        )

        # Step 1 — Pre-normalization field validation.
        raw_dict: dict[str, Any] = raw_log.model_dump()
        try:
            validate_raw_log_fields(raw_dict)
        except ValidationError:
            logger.warning(
                "Log rejected at validation stage | log_id=%s | service=%s",
                raw_log.log_id,
                raw_log.service,
            )
            raise

        # Step 2 — Normalize the timestamp.
        try:
            normalized_timestamp = normalize_timestamp(raw_log.timestamp)
        except ValueError as exc:
            raise ValidationError(
                message=f"Unparseable timestamp in log '{raw_log.log_id}'.",
                detail={
                    "log_id": raw_log.log_id,
                    "timestamp": str(raw_log.timestamp),
                    "reason": str(exc),
                },
            ) from exc

        # Step 3 — Normalize the message (raises on blank/None).
        try:
            normalized_message = normalize_message(raw_log.message)
        except ValueError as exc:
            raise ValidationError(
                message=str(exc),
                detail={"log_id": raw_log.log_id},
            ) from exc

        # Steps 4–6 — Normalize remaining fields (never raise).
        log_id = normalize_log_id(raw_log.log_id)
        service = normalize_service(raw_log.service)
        component = normalize_component(raw_log.component)
        log_level = normalize_log_level(raw_log.log_level)

        # Step 7 — Extract a log template and its variable parameters.
        template, parameters = extract_template(normalized_message)

        # Step 8 — Assemble and return the NormalizedLog.
        normalized = NormalizedLog(
            log_id=log_id,
            timestamp=normalized_timestamp,
            service=service,
            component=component,
            log_level=log_level,
            message=normalized_message,
            template=template,
            parameters=parameters,
            metadata=dict(raw_log.metadata),  # Preserve original metadata intact.
        )

        logger.debug(
            "Log normalized | log_id=%s | service=%s | level=%s | template_found=%s",
            normalized.log_id,
            normalized.service,
            normalized.log_level,
            template is not None,
        )

        return normalized

    def process_batch(self, raw_logs: list[RawLog]) -> list[NormalizedLog]:
        """
        Transform a batch of RawLog objects into deduplicated NormalizedLog objects.

        Logs that fail validation are individually skipped and counted.
        They are logged at WARNING level with their log_id for traceability.
        The method never raises on partial batch failures — it returns the
        successfully normalized and deduplicated subset.

        Parameters
        ----------
        raw_logs:
            A list of RawLog objects to normalize.

        Returns
        -------
        list[NormalizedLog]
            Validated, normalized, and deduplicated logs in original order
            (excluding failed entries).
        """
        if not raw_logs:
            logger.info("Empty batch received — returning empty list.")
            return []

        logger.info("Starting batch normalization | count=%d", len(raw_logs))

        normalized: list[NormalizedLog] = []
        failed_count = 0

        for raw_log in raw_logs:
            try:
                normalized.append(self.process(raw_log))
            except ValidationError as exc:
                failed_count += 1
                logger.warning(
                    "Log skipped | log_id=%s | service=%s | reason=%s",
                    raw_log.log_id,
                    raw_log.service,
                    exc.message,
                )

        logger.info(
            "Batch normalization complete | total=%d | normalized=%d | failed=%d",
            len(raw_logs),
            len(normalized),
            failed_count,
        )

        # Deduplication is always applied after normalization.
        return deduplicate(normalized)
