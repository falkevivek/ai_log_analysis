"""
AI Analysis Pipeline Orchestrator
==================================
The central orchestration layer coordinates the execution of all pipeline engines
stage-by-stage. Maintains complete independence of each engine, tracks execution
durations, and builds a comprehensive PipelineResult.

Pipeline flow:
Raw Logs -> LogProcessing -> Observation -> EventIntelligence -> TimelineIntelligence ->
IncidentBuilder -> ContextEnrichment -> EvidenceBuilder -> LlmReasoning -> Recommendation

Resilience
----------
- Critical stages: LogProcessing, Observation, EventIntelligence, TimelineIntelligence, IncidentBuilder.
  Any exception or validation failure halts execution immediately.
- Enriched stages: ContextEnrichment, EvidenceBuilder, LlmReasoning, Recommendation.
  If ContextEnrichment fails, the pipeline proceeds with a safe default Context.
  If LlmReasoning or Recommendation fails, the pipeline returns a PARTIAL_FAILURE status
  with whatever structures were successfully completed.
"""

from __future__ import annotations

import logging
import time
import uuid
from typing import Any, Optional

# Import domain schemas
from app.schemas.domain import (
    RawLog,
    NormalizedLog,
    Observation,
    Event,
    Timeline,
    Incident,
    Context,
    Evidence,
    Diagnosis,
    Recommendation,
    PipelineResult
)
from app.exceptions.custom_exceptions import ValidationError

# Import all engines
from app.engines.log_processing import LogProcessingEngine
from app.engines.observation import ObservationEngine
from app.engines.event_intelligence import EventIntelligenceEngine
from app.engines.timeline_intelligence import TimelineIntelligenceEngine
from app.engines.incident_builder import IncidentBuilder
from app.engines.context_enrichment import ContextEnrichmentEngine
from app.engines.evidence_builder import EvidenceBuilder
from app.engines.llm_reasoning import LlmReasoningEngine
from app.engines.recommendation import RecommendationEngine

logger = logging.getLogger("ai_analysis_engine.orchestrator.pipeline")


class AIAnalysisOrchestrator:
    """Coordinates independent engines to execute the unified diagnostic pipeline."""

    def __init__(
        self,
        log_processor: Optional[LogProcessingEngine] = None,
        observation_engine: Optional[ObservationEngine] = None,
        event_engine: Optional[EventIntelligenceEngine] = None,
        timeline_engine: Optional[TimelineIntelligenceEngine] = None,
        incident_builder: Optional[IncidentBuilder] = None,
        context_enricher: Optional[ContextEnrichmentEngine] = None,
        evidence_builder: Optional[EvidenceBuilder] = None,
        llm_engine: Optional[LlmReasoningEngine] = None,
        recommendation_engine: Optional[RecommendationEngine] = None
    ) -> None:
        """
        Initialize the orchestrator with customizable engine instances.
        """
        self.log_processor = log_processor or LogProcessingEngine()
        self.observation_engine = observation_engine or ObservationEngine()
        self.event_engine = event_engine or EventIntelligenceEngine()
        self.timeline_engine = timeline_engine or TimelineIntelligenceEngine()
        self.incident_builder = incident_builder or IncidentBuilder()
        self.context_enricher = context_enricher or ContextEnrichmentEngine()
        self.evidence_builder = evidence_builder or EvidenceBuilder()
        self.llm_engine = llm_engine or LlmReasoningEngine()
        self.recommendation_engine = recommendation_engine or RecommendationEngine()

        logger.info("AIAnalysisOrchestrator successfully initialized with all engines.")

    def run_pipeline(
        self,
        raw_logs: list[RawLog],
        metadata_overrides: Optional[dict[str, Any]] = None
    ) -> PipelineResult:
        """
        Run the complete pipeline against batch raw logs.

        Parameters
        ----------
        raw_logs:
            List of input RawLog models.
        metadata_overrides:
            Optional parameter dictionary passed down to IncidentBuilder and ContextEnricher.

        Returns
        -------
        PipelineResult
            The unified execution result containing all outputs and timings stats.
        """
        session_id = str(uuid.uuid4())
        logger.info("Starting pipeline execution | Session ID=%s | logs count=%d", session_id, len(raw_logs))

        execution_stats: dict[str, float] = {}
        
        # Pipeline State
        normalized_logs: Optional[list[NormalizedLog]] = None
        observations: Optional[list[Observation]] = None
        events: Optional[list[Event]] = None
        timeline: Optional[Timeline] = None
        incident: Optional[Incident] = None
        context: Optional[Context] = None
        evidence: Optional[Evidence] = None
        diagnosis: Optional[Diagnosis] = None
        recommendation: Optional[Recommendation] = None

        # =====================================================================
        # Stage 1: Log Ingestion & Normalization (CRITICAL)
        # =====================================================================
        start_time = time.perf_counter()
        try:
            if not raw_logs:
                raise ValidationError(message="Input raw logs list cannot be empty.", detail={"session_id": session_id})
            normalized_logs = self.log_processor.process_batch(raw_logs)
            if not normalized_logs:
                raise ValidationError(message="Log Processing returned empty normalized logs.", detail={"session_id": session_id})
            execution_stats["LogProcessing"] = (time.perf_counter() - start_time) * 1000.0
        except Exception as exc:
            logger.exception("Log Processing failed critically. Halting pipeline.")
            return PipelineResult(
                session_id=session_id,
                execution_stats=execution_stats,
                status="FAILED",
                error_message=f"LogProcessing stage failed critically: {str(exc)}"
            )

        # =====================================================================
        # Stage 2: Observation Classification (CRITICAL)
        # =====================================================================
        start_time = time.perf_counter()
        try:
            observations = self.observation_engine.process_batch(normalized_logs)
            if not observations:
                raise ValidationError(message="Observation Engine returned empty observations.", detail={"session_id": session_id})
            execution_stats["Observation"] = (time.perf_counter() - start_time) * 1000.0
        except Exception as exc:
            logger.exception("Observation Engine failed critically. Halting pipeline.")
            return PipelineResult(
                session_id=session_id,
                execution_stats=execution_stats,
                status="FAILED",
                error_message=f"Observation stage failed critically: {str(exc)}"
            )

        # =====================================================================
        # Stage 3 & 4: Correlation & Event Intelligence (CRITICAL)
        # =====================================================================
        start_time = time.perf_counter()
        try:
            events = self.event_engine.process_observations(observations)
            if not events:
                raise ValidationError(message="Event Intelligence returned empty events list.", detail={"session_id": session_id})
            execution_stats["EventIntelligence"] = (time.perf_counter() - start_time) * 1000.0
        except Exception as exc:
            logger.exception("Event Intelligence failed critically. Halting pipeline.")
            return PipelineResult(
                session_id=session_id,
                execution_stats=execution_stats,
                status="FAILED",
                error_message=f"EventIntelligence stage failed critically: {str(exc)}"
            )

        # =====================================================================
        # Stage 5: Timeline Intelligence Reconstruction (CRITICAL)
        # =====================================================================
        start_time = time.perf_counter()
        try:
            timeline = self.timeline_engine.process_events(events)
            execution_stats["TimelineIntelligence"] = (time.perf_counter() - start_time) * 1000.0
        except Exception as exc:
            logger.exception("Timeline Intelligence failed critically. Halting pipeline.")
            return PipelineResult(
                session_id=session_id,
                execution_stats=execution_stats,
                status="FAILED",
                error_message=f"TimelineIntelligence stage failed critically: {str(exc)}"
            )

        # =====================================================================
        # Stage 6: Incident Construction (CRITICAL)
        # =====================================================================
        start_time = time.perf_counter()
        try:
            incident = self.incident_builder.build_incident(timeline, metadata_overrides)
            execution_stats["IncidentBuilder"] = (time.perf_counter() - start_time) * 1000.0
        except Exception as exc:
            logger.exception("Incident Builder failed critically. Halting pipeline.")
            return PipelineResult(
                session_id=session_id,
                execution_stats=execution_stats,
                status="FAILED",
                error_message=f"IncidentBuilder stage failed critically: {str(exc)}"
            )

        # =====================================================================
        # Stage 7: Context Enrichment (NON-CRITICAL FALLBACK)
        # =====================================================================
        start_time = time.perf_counter()
        try:
            context = self.context_enricher.enrich_incident(incident)
            execution_stats["ContextEnrichment"] = (time.perf_counter() - start_time) * 1000.0
        except Exception as exc:
            logger.warning("Context Enrichment failed. Falling back to default empty context parameters.", exc_info=True)
            # Create a simple fallback Context to avoid halting downstream stages
            try:
                context = Context(
                    incident=incident,
                    project_name=incident.incident_metadata.project or "Fallback Project",
                    environment=incident.incident_metadata.environment or "production",
                    application=incident.incident_metadata.application or "Fallback Application",
                    services=incident.affected_services,
                    components=incident.affected_components,
                    metadata={"error": f"Enrichment failure: {str(exc)}"}
                )
                execution_stats["ContextEnrichment"] = (time.perf_counter() - start_time) * 1000.0
            except Exception as context_exc:
                logger.error("Failed to construct fallback Context record. Halting.", exc_info=True)
                return PipelineResult(
                    session_id=session_id,
                    incident=incident,
                    execution_stats=execution_stats,
                    status="PARTIAL_FAILURE",
                    error_message=f"ContextEnrichment stage crashed completely: {str(context_exc)}"
                )

        # =====================================================================
        # Stage 8: Evidence Package Assembly (NON-CRITICAL FALLBACK)
        # =====================================================================
        start_time = time.perf_counter()
        try:
            evidence = self.evidence_builder.build_evidence(incident, context)
            execution_stats["EvidenceBuilder"] = (time.perf_counter() - start_time) * 1000.0
        except Exception as exc:
            logger.warning("Evidence Builder failed. Halting diagnostic stages. Returning built incident.", exc_info=True)
            return PipelineResult(
                session_id=session_id,
                incident=incident,
                context=context,
                execution_stats=execution_stats,
                status="PARTIAL_FAILURE",
                error_message=f"EvidenceBuilder stage failed: {str(exc)}"
            )

        # =====================================================================
        # Stage 9: LLM Diagnostic Reasoning (NON-CRITICAL FALLBACK)
        # =====================================================================
        start_time = time.perf_counter()
        try:
            diagnosis = self.llm_engine.diagnose(evidence)
            execution_stats["LlmReasoning"] = (time.perf_counter() - start_time) * 1000.0
        except Exception as exc:
            logger.warning("LLM Reasoning failed. Halting recommendation stages.", exc_info=True)
            return PipelineResult(
                session_id=session_id,
                incident=incident,
                context=context,
                evidence=evidence,
                execution_stats=execution_stats,
                status="PARTIAL_FAILURE",
                error_message=f"LlmReasoning stage failed: {str(exc)}"
            )

        # =====================================================================
        # Stage 10: Recommendation generation (NON-CRITICAL FALLBACK)
        # =====================================================================
        start_time = time.perf_counter()
        try:
            recommendation = self.recommendation_engine.generate_recommendations(diagnosis, evidence)
            execution_stats["Recommendation"] = (time.perf_counter() - start_time) * 1000.0
        except Exception as exc:
            logger.warning("Recommendation Engine failed.", exc_info=True)
            return PipelineResult(
                session_id=session_id,
                incident=incident,
                context=context,
                evidence=evidence,
                diagnosis=diagnosis,
                execution_stats=execution_stats,
                status="PARTIAL_FAILURE",
                error_message=f"Recommendation stage failed: {str(exc)}"
            )

        # Pipeline successful
        logger.info("Pipeline executed successfully | Session ID=%s", session_id)
        return PipelineResult(
            session_id=session_id,
            incident=incident,
            context=context,
            evidence=evidence,
            diagnosis=diagnosis,
            recommendation=recommendation,
            execution_stats=execution_stats,
            status="SUCCESS"
        )
