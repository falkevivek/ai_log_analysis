# Recommendation Engine package
# Exposes the main RecommendationEngine and BaseRecommendationStrategy interface.
from app.engines.recommendation.engine import RecommendationEngine
from app.engines.recommendation.strategies.base import BaseRecommendationStrategy

__all__ = ["RecommendationEngine", "BaseRecommendationStrategy"]
