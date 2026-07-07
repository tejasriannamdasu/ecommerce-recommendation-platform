"""
Process-wide holder for loaded ML models. Models are trained offline
(see app.ml.train_pipeline) and loaded once at API startup so requests
don't pay the cost of re-fitting TF-IDF/NMF/FAISS on every call.
"""
from app.ml.content_based import ContentBasedRecommender
from app.ml.collaborative_filtering import CollaborativeFilteringRecommender
from app.ml.semantic_search import SemanticSearchEngine
from app.ml.hybrid import HybridRecommender
from app.config import get_settings
import logging
import os

logger = logging.getLogger(__name__)


class MLRegistry:
    def __init__(self):
        self.content_model: ContentBasedRecommender | None = None
        self.collab_model: CollaborativeFilteringRecommender | None = None
        self.semantic_engine: SemanticSearchEngine | None = None
        self.hybrid_model: HybridRecommender | None = None

    def load(self):
        settings = get_settings()
        path = settings.ML_MODELS_DIR
        try:
            self.content_model = ContentBasedRecommender.load(path)
            self.collab_model = CollaborativeFilteringRecommender.load(path)
            self.semantic_engine = SemanticSearchEngine.load(path)
            self.hybrid_model = HybridRecommender(
                self.content_model, self.collab_model,
                content_weight=settings.CONTENT_WEIGHT, collab_weight=settings.COLLAB_WEIGHT,
            )
            logger.info("ML models loaded successfully from %s", path)
        except FileNotFoundError:
            logger.warning(
                "No trained models found at %s. Run `python -m app.ml.train_pipeline` "
                "(or scripts/train_models.py) after seeding data.", path
            )


ml_registry = MLRegistry()
