"""
UI and JavaScript Rules
========================
Detects frontend rendering failures and JavaScript runtime exceptions.

Observation Types:
  UI_RENDERING_FAILURE  — base severity MEDIUM
  JAVASCRIPT_EXCEPTION  — base severity MEDIUM
"""

from __future__ import annotations

from app.engines.observation.rules.base import ObservationRule
from app.schemas.domain import NormalizedLog


class UiRenderingFailureRule(ObservationRule):
    """
    Fires when a log contains signals of a frontend UI rendering failure.

    Covers: React/Vue/Angular component errors, DOM failures,
    server-side rendering (SSR) hydration errors, and general UI crash patterns.
    """

    _KEYWORDS: tuple[tuple[str, float], ...] = (
        ("rendering failed", 0.80),
        ("render failed", 0.80),
        ("render error", 0.70),
        ("component crashed", 0.80),
        ("component error", 0.55),
        ("hydration error", 0.80),
        ("hydration failed", 0.80),
        ("dom exception", 0.70),
        ("dom error", 0.65),
        ("ui error", 0.60),
        ("ui crash", 0.75),
        ("react error boundary", 0.85),
        ("react error", 0.65),
        ("vue error", 0.65),
        ("angular error", 0.65),
        ("template error", 0.55),
        ("rendering", 0.15),
        ("dom", 0.15),
        ("component", 0.10),
    )

    @property
    def observation_type(self) -> str:
        return "UI_RENDERING_FAILURE"

    @property
    def base_severity(self) -> str:
        return "MEDIUM"

    def match_confidence(self, log: NormalizedLog) -> float:
        return self._compute_confidence(log.message, self._KEYWORDS)

    def describe(self, log: NormalizedLog) -> str:
        try:
            return (
                f"UI rendering failure detected in component '{log.component}' "
                f"(service: '{log.service}'). "
                f"Log: {log.message[:150]}"
            )
        except Exception:
            return "UI rendering failure detected."


class JavaScriptExceptionRule(ObservationRule):
    """
    Fires when a log contains signals of a JavaScript runtime exception.

    Covers: uncaught exceptions, TypeError, ReferenceError, SyntaxError,
    unhandled promise rejections, null/undefined dereferences, and stack overflows.
    """

    _KEYWORDS: tuple[tuple[str, float], ...] = (
        ("uncaught exception", 0.85),
        ("uncaught error", 0.85),
        ("unhandled promise rejection", 0.90),
        ("unhandled rejection", 0.80),
        ("cannot read property", 0.80),
        ("cannot read properties", 0.80),
        ("is not a function", 0.75),
        ("is not defined", 0.70),
        ("undefined is not", 0.75),
        ("null is not", 0.75),
        ("typeerror", 0.65),
        ("referenceerror", 0.65),
        ("syntaxerror", 0.65),
        ("rangeerror", 0.65),
        ("null pointer", 0.60),
        ("stack overflow", 0.70),
        ("maximum call stack", 0.75),
        ("javascript error", 0.65),
        ("js error", 0.55),
        ("exception", 0.20),
        ("traceback", 0.20),
        ("stack trace", 0.20),
    )

    @property
    def observation_type(self) -> str:
        return "JAVASCRIPT_EXCEPTION"

    @property
    def base_severity(self) -> str:
        return "MEDIUM"

    def match_confidence(self, log: NormalizedLog) -> float:
        return self._compute_confidence(log.message, self._KEYWORDS)


    def describe(self, log: NormalizedLog) -> str:
        try:
            return (
                f"JavaScript exception detected in component '{log.component}' "
                f"(service: '{log.service}'). "
                f"Log: {log.message[:150]}"
            )
        except Exception:
            return "JavaScript exception detected."
