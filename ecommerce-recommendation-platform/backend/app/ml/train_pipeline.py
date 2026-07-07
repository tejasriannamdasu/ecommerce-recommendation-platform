"""
End-to-end ML training pipeline:
  1. Data Collection   -> pull products/interactions/ratings from Postgres
  2. Data Cleaning     -> drop nulls/dupes, normalize text, clip outlier weights
  3. Feature Engineering -> build text corpus, weighted interaction matrix
  4. Model Training     -> fit content-based, collaborative, semantic models
  5. Model Evaluation   -> precision@k on a held-out interaction split
  6. Persistence        -> save all models to ML_MODELS_DIR for the API to load

Run standalone:  python -m app.ml.train_pipeline
"""
from __future__ import annotations
import logging
import pandas as pd
from sqlalchemy.orm import Session
from sqlalchemy import func

from app.database import SessionLocal
from app.config import get_settings
from app.models.product import Product, Category
from app.models.interaction import UserInteraction, Rating
from app.ml.content_based import ContentBasedRecommender
from app.ml.collaborative_filtering import CollaborativeFilteringRecommender
from app.ml.semantic_search import SemanticSearchEngine
from app.ml.evaluate import precision_at_k

logging.basicConfig(level=logging.INFO, format="%(asctime)s | %(levelname)s | %(message)s")
logger = logging.getLogger(__name__)

INTERACTION_WEIGHTS = {"view": 1.0, "click": 2.0, "purchase": 5.0, "wishlist": 3.0}


def collect_products(db: Session) -> pd.DataFrame:
    rows = (
        db.query(Product, Category.name.label("category_name"))
        .outerjoin(Category, Product.category_id == Category.id)
        .all()
    )
    data = [
        {
            "id": p.id,
            "title": p.title,
            "description": p.description or "",
            "category": cat_name or "",
            "tags": p.tags or "",
        }
        for p, cat_name in rows
    ]
    return pd.DataFrame(data)


def collect_interactions(db: Session) -> pd.DataFrame:
    interactions = db.query(UserInteraction).all()
    rows = [
        {
            "user_id": i.user_id,
            "product_id": i.product_id,
            "weight": INTERACTION_WEIGHTS.get(i.interaction_type.value, 1.0) * (i.weight or 1.0),
        }
        for i in interactions
    ]
    ratings = db.query(Rating).all()
    for r in ratings:
        rows.append({"user_id": r.user_id, "product_id": r.product_id, "weight": r.score})

    df = pd.DataFrame(rows)
    if df.empty:
        return df
    # Data cleaning: aggregate duplicate (user, product) signals, clip outliers
    df = df.groupby(["user_id", "product_id"], as_index=False)["weight"].sum()
    df["weight"] = df["weight"].clip(upper=df["weight"].quantile(0.99))
    return df


def run_pipeline():
    settings = get_settings()
    db = SessionLocal()
    try:
        logger.info("Step 1/6: Collecting data from PostgreSQL...")
        products_df = collect_products(db)
        interactions_df = collect_interactions(db)
        logger.info(f"  -> {len(products_df)} products, {len(interactions_df)} aggregated interactions")

        logger.info("Step 2/6: Cleaning data...")
        products_df = products_df.drop_duplicates(subset="id").fillna("")

        logger.info("Step 3/6: Feature engineering (handled inside model .fit calls)")

        logger.info("Step 4/6: Training Content-Based model (TF-IDF)...")
        content_model = ContentBasedRecommender().fit(products_df)

        logger.info("Step 5/6: Training Collaborative Filtering model (NMF)...")
        if not interactions_df.empty and interactions_df["user_id"].nunique() > 1:
            collab_model = CollaborativeFilteringRecommender().fit(interactions_df)
            precision = precision_at_k(collab_model, interactions_df, k=10)
            logger.info(f"  -> Precision@10 (held-out): {precision:.4f}")
        else:
            collab_model = CollaborativeFilteringRecommender()
            logger.warning("  -> Not enough interaction data to train collaborative model; skipping")

        logger.info("Training Semantic Search index...")
        semantic_engine = SemanticSearchEngine(model_name=settings.SEMANTIC_MODEL_NAME).fit(products_df)
        logger.info(f"  -> Semantic engine mode: {semantic_engine.mode}")

        logger.info("Step 6/6: Persisting models to %s", settings.ML_MODELS_DIR)
        content_model.save(settings.ML_MODELS_DIR)
        collab_model.save(settings.ML_MODELS_DIR)
        semantic_engine.save(settings.ML_MODELS_DIR)

        # Precompute popularity scores for cold-start ranking
        pop = interactions_df.groupby("product_id")["weight"].sum() if not interactions_df.empty else pd.Series(dtype=float)
        for product in db.query(Product).all():
            product.popularity_score = float(pop.get(product.id, 0.0))
        db.commit()

        logger.info("Training pipeline complete.")
    finally:
        db.close()


if __name__ == "__main__":
    run_pipeline()
