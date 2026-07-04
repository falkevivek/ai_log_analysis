"""
Logging Configuration
======================
Configures the Python standard-library logging system for the platform.

Call ``configure_logging()`` exactly once at application startup, before any
logger is used. Application code should always use:

    import logging
    logger = logging.getLogger(__name__)

Root logger is set to WARNING so third-party libraries stay quiet.
The ``ai_analysis_engine`` logger inherits the configured level.
"""

from __future__ import annotations

import logging
import sys


def configure_logging(log_level: str = "INFO") -> None:
    """
    Set up stdout logging for the platform.

    Parameters
    ----------
    log_level:
        One of DEBUG | INFO | WARNING | ERROR | CRITICAL.
        Defaults to INFO.
    """
    level = logging.getLevelName(log_level.upper())

    formatter = logging.Formatter(
        fmt="%(asctime)s | %(levelname)-8s | %(name)s | %(message)s",
        datefmt="%Y-%m-%dT%H:%M:%S",
    )

    handler = logging.StreamHandler(sys.stdout)
    handler.setFormatter(formatter)
    handler.setLevel(level)

    # Root logger at WARNING — keeps third-party libraries quiet.
    root = logging.getLogger()
    if not root.handlers:
        root.setLevel(logging.WARNING)
        root.addHandler(handler)

    # Application logger inherits the configured level.
    app_logger = logging.getLogger("ai_analysis_engine")
    app_logger.setLevel(level)
    app_logger.propagate = True

    # Quieten particularly chatty libraries.
    logging.getLogger("uvicorn.access").setLevel(logging.WARNING)
