"""
Rule-Based Recommendation Strategy
==================================
Matches root causes, error codes, and affected components against registered
onboarding rules to produce deterministic, actionable suggestions.
"""

from __future__ import annotations

import logging
from typing import Any
from pydantic import BaseModel, Field

from app.engines.recommendation.strategies.base import BaseRecommendationStrategy
from app.schemas.domain import Diagnosis, Evidence

logger = logging.getLogger("ai_analysis_engine.engines.recommendation.strategies.rule_based")


class RecommendationRuleTemplate(BaseModel):
    """A template mapping incident traits to specific remediation actions."""

    trigger_type: str = Field(..., description="Trigger category: keyword, error_code, or component")
    trigger_values: list[str] = Field(..., description="Target matches for the trigger trigger_type (case-insensitive)")
    immediate_action: str = Field(..., description="Quick-fix suggestion to restore service")
    investigation_steps: list[str] = Field(default_factory=list, description="Target investigation checklist")
    permanent_solution: str = Field(..., description="Long-term structural fix suggestion")
    prevention_suggestions: list[str] = Field(default_factory=list, description="Suggestions to avoid future failures")
    known_error_references: list[str] = Field(default_factory=list, description="Related known error codes")
    historical_incident_references: list[str] = Field(default_factory=list, description="Similar past incidents code refs")
    confidence_score: float = Field(0.9, ge=0.0, le=1.0, description="Confidence level of this match")


class RuleBasedRecommendationConfig(BaseModel):
    """Configuration holding registered rules list and defaults."""

    rules: list[RecommendationRuleTemplate] = Field(default_factory=list)
    
    # Generic default recommendation if no rule triggers match
    default_immediate_action: str = "Collect process dumps and inspect routing filters in deployment pipelines."
    default_investigation_steps: list[str] = Field(
        default_factory=lambda: [
            "Verify network routing table configurations.",
            "Compare active config flags with previous deployment release revision settings."
        ]
    )
    default_permanent_solution: str = "Perform full structural load profiling of system dependencies."
    default_prevention_suggestions: list[str] = Field(
        default_factory=lambda: [
            "Implement canary deployment models.",
            "Configure automatic alerts thresholds for connection pool limits."
        ]
    )
    default_confidence_score: float = 0.5


class RuleBasedRecommendationStrategy(BaseRecommendationStrategy):
    """Analyzes diagnostic attributes and matches templates deterministically."""

    def __init__(self, config: Optional[RuleBasedRecommendationConfig] = None) -> None:
        """
        Initialize the Rule-Based Strategy.

        Parameters
        ----------
        config:
            Optional config containing rules catalog. Defaults to standard library rules.
        """
        self.config = config or self._get_default_onboarding_rules()
        logger.info(
            "RuleBasedRecommendationStrategy initialized with %d registered templates",
            len(self.config.rules)
        )

    @property
    def strategy_name(self) -> str:
        return "RULE_BASED_STRATEGY"

    def recommend(self, diagnosis: Diagnosis, evidence: Evidence) -> dict[str, Any]:
        """
        Match diagnosis and evidence features, consolidating recommendations.
        """
        matched_rules: list[RecommendationRuleTemplate] = []

        # Analyze traits
        root_cause_lower = diagnosis.root_cause.lower()
        explanation_lower = diagnosis.explanation.lower()
        active_components = {c.lower().strip() for c in evidence.affected_components}
        active_errors = {err.lower().strip() for err in evidence.error_codes + evidence.known_errors}

        # Scan registered rules
        for rule in self.config.rules:
            triggered = False
            
            # 1. Trigger by keyword match in root cause or explanation
            if rule.trigger_type == "keyword":
                for kw in rule.trigger_values:
                    kw_clean = kw.lower().strip()
                    if kw_clean in root_cause_lower or kw_clean in explanation_lower:
                        triggered = True
                        break

            # 2. Trigger by error code match
            elif rule.trigger_type == "error_code":
                for val in rule.trigger_values:
                    val_clean = val.lower().strip()
                    if val_clean in active_errors:
                        triggered = True
                        break

            # 3. Trigger by component match
            elif rule.trigger_type == "component":
                for val in rule.trigger_values:
                    val_clean = val.lower().strip()
                    if val_clean in active_components:
                        triggered = True
                        break

            if triggered:
                matched_rules.append(rule)

        # Handle fallback if no rules match
        if not matched_rules:
            logger.info("No recommendation rules matched. Applying default onboarding templates.")
            return {
                "immediate_action": self.config.default_immediate_action,
                "investigation_steps": self.config.default_investigation_steps,
                "permanent_solution": self.config.default_permanent_solution,
                "prevention_suggestions": self.config.default_prevention_suggestions,
                "known_error_references": sorted(list(set(evidence.known_errors))),
                "historical_incident_references": sorted(list(set(evidence.historical_references))),
                "recommendation_confidence": self.config.default_confidence_score
            }

        # Consolidate matched recommendations
        logger.info("%d recommendation rules matched. Consolidating...", len(matched_rules))
        
        # Lists aggregation (with de-duplication)
        investigation_steps = []
        prevention_suggestions = []
        known_error_references = list(evidence.known_errors)
        historical_incident_references = list(evidence.historical_references)
        
        # Select best rule based on highest confidence score for quick-fix / long-term suggestions
        best_rule = max(matched_rules, key=lambda r: r.confidence_score)
        
        for rule in matched_rules:
            investigation_steps.extend(rule.investigation_steps)
            prevention_suggestions.extend(rule.prevention_suggestions)
            known_error_references.extend(rule.known_error_references)
            historical_incident_references.extend(rule.historical_incident_references)

        # De-duplicate lists
        investigation_steps = sorted(list(set(investigation_steps)))
        prevention_suggestions = sorted(list(set(prevention_suggestions)))
        known_error_references = sorted(list(set(known_error_references)))
        historical_incident_references = sorted(list(set(historical_incident_references)))

        # Average confidence score across all matched rules
        avg_confidence = sum(r.confidence_score for r in matched_rules) / len(matched_rules)

        return {
            "immediate_action": best_rule.immediate_action,
            "investigation_steps": investigation_steps,
            "permanent_solution": best_rule.permanent_solution,
            "prevention_suggestions": prevention_suggestions,
            "known_error_references": known_error_references,
            "historical_incident_references": historical_incident_references,
            "recommendation_confidence": float(min(1.0, max(0.0, avg_confidence)))
        }

    @staticmethod
    def _get_default_onboarding_rules() -> RuleBasedRecommendationConfig:
        """Standard default onboarding catalog rules for database timeouts and authorization issues."""
        db_rule = RecommendationRuleTemplate(
            trigger_type="keyword",
            trigger_values=["database", "postgres", "connection pool", "pool exhaustion"],
            immediate_action="Force restart database connection pools and scale worker replicas.",
            investigation_steps=[
                "Analyze pg_stat_activity view for long-running locked queries.",
                "Check for open transaction leaks in auth application repositories."
            ],
            permanent_solution="Increase the max_connections limits on database server and client configurations.",
            prevention_suggestions=[
                "Implement strict connection leak detection timers.",
                "Introduce circuit breaker rules on API endpoints executing database writes."
            ],
            known_error_references=["ERR_POOL_EXHAUSTED", "ERR_CONNECTION_TIMEOUT"],
            historical_incident_references=["INC-2026-0043"],
            confidence_score=0.95
        )

        auth_rule = RecommendationRuleTemplate(
            trigger_type="error_code",
            trigger_values=["ERR_AUTH_EXPIRED_TOKEN", "ERR_CREDENTIALS_MISMATCH"],
            immediate_action="Clear token replication cache and flush authentication gateway caches.",
            investigation_steps=[
                "Verify system timezone offsets matching auth gateway servers.",
                "Inspect authentication filter stack logs for cipher mismatch errors."
            ],
            permanent_solution="Introduce refresh token token-rotation patterns to handle transient expiration failures.",
            prevention_suggestions=[
                "Set token replication cache eviction limits safely.",
                "Implement automatic backoff and retry limits on gateway credentials checks."
            ],
            known_error_references=["ERR_AUTH_EXPIRED_TOKEN"],
            historical_incident_references=["INC-2026-0105"],
            confidence_score=0.90
        )

        return RuleBasedRecommendationConfig(rules=[db_rule, auth_rule])
