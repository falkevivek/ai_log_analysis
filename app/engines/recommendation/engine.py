"""
Recommendation Engine
=====================
Stage 10 of the AI Analysis pipeline.

Receives a completed Diagnosis and Evidence Package, coordinating with a pluggable
BaseRecommendationStrategy (defaults to RuleBasedRecommendationStrategy) to
generate structured operational recommendations (immediate mitigation check,
investigation paths, long-term preventions) for developers.

Responsibilities
----------------
1. Receive Diagnosis and Evidence Package.
2. Verify parameter validity.
3. Coordinate execution across the configured RecommendationStrategy.
4. Auto-generate Recommendation ID and timestamp.
5. Construct and return a validated Recommendation domain object.

This engine does NOT
--------------------
- Perform root cause analysis.
- Modify the Diagnosis or Evidence package.
- Call external systems or learn from user feedback.
"""

from __future__ import annotations

import logging
import uuid
from datetime import datetime, timezone
from typing import Optional

from app.engines.recommendation.strategies import RuleBasedRecommendationStrategy, BaseRecommendationStrategy
from app.exceptions.custom_exceptions import ValidationError
from app.schemas.domain import Diagnosis, Evidence, Recommendation

logger = logging.getLogger("ai_analysis_engine.engines.recommendation.engine")


class RecommendationEngine:
    """Orchestrates Recommendation strategies to build actionable remediation items."""

    def __init__(self, strategy: Optional[BaseRecommendationStrategy] = None) -> None:
        """
        Initialize the Recommendation Engine.

        Parameters
        ----------
        strategy:
            The pluggable recommendation generation strategy.
            Defaults to RuleBasedRecommendationStrategy.
        """
        self.strategy = strategy or RuleBasedRecommendationStrategy()
        logger.info(
            "RecommendationEngine initialized with strategy: %s",
            self.strategy.strategy_name
        )

    def generate_recommendations(
        self,
        diagnosis: Diagnosis,
        evidence: Evidence
    ) -> Recommendation:
        """
        Generate operational recommendations for remediation.

        Parameters
        ----------
        diagnosis:
            The established AI Diagnosis record.
        evidence:
            The consolidated Evidence Package.

        Returns
        -------
        Recommendation
            The validated Recommendation object containing actionable remediation checklists.

        Raises
        ------
        ValidationError
            If parameters are empty or invalid, or if Pydantic validation fails.
        """
        if not diagnosis:
            raise ValidationError(
                message="Cannot generate recommendations from an empty or missing Diagnosis.",
                detail={"engine": "RecommendationEngine"}
            )
        if not evidence:
            raise ValidationError(
                message="Cannot generate recommendations from an empty or missing Evidence Package.",
                detail={"engine": "RecommendationEngine"}
            )

        logger.debug(
            "Generating recommendations | root_cause='%s' | strategy=%s",
            diagnosis.root_cause,
            self.strategy.strategy_name
        )

        # Delegate recommendation generation to the strategy
        try:
            results = self.strategy.recommend(diagnosis, evidence)
        except Exception as exc:
            raise ValidationError(
                message=f"Recommendation strategy execution failed: {str(exc)}",
                detail={"strategy": self.strategy.strategy_name}
            ) from exc

        # Construct validated Recommendation domain model
        try:
            recommendation = Recommendation(
                recommendation_id=str(uuid.uuid4()),
                immediate_action=results["immediate_action"],
                investigation_steps=results["investigation_steps"],
                permanent_solution=results["permanent_solution"],
                prevention_suggestions=results["prevention_suggestions"],
                known_error_references=results["known_error_references"],
                historical_incident_references=results["historical_incident_references"],
                recommendation_confidence=results["recommendation_confidence"],
                generated_at=datetime.now(timezone.utc),
                additional_notes=results.get("additional_notes")
            )
        except Exception as exc:
            raise ValidationError(
                message=f"Failed to validate Recommendation domain contract: {str(exc)}",
                detail={"results": results}
            ) from exc

        logger.info(
            "Recommendations generated successfully | ID=%s | confidence=%.2f",
            recommendation.recommendation_id,
            recommendation.recommendation_confidence
        )
        return recommendation
