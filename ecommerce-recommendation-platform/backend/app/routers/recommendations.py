"""
Recommendation endpoints: personalized (hybrid), similar products,
and trending/popular (cold-start fallback for anonymous or new users).
"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.product import Product
from app.models.interaction import UserInteraction
from app.schemas.product import ProductOut, RecommendationItem, RecommendationResponse
from app.auth.dependencies import get_current_user
from app.models.user import User
from app.ml_state import ml_registry
from app.utils.cache import cache_get, cache_set

router = APIRouter(prefix="/recommendations", tags=["Recommendations"])


@router.get("/personalized", response_model=RecommendationResponse)
def personalized(limit: int = 10, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    cache_key = f"reco:personalized:{current_user.id}:{limit}"
    cached = cache_get(cache_key)
    if cached:
        return cached

    if ml_registry.hybrid_model is None:
        raise HTTPException(status_code=503, detail="Recommendation models not loaded yet")

    recent = (
        db.query(UserInteraction.product_id)
        .filter(UserInteraction.user_id == current_user.id)
        .order_by(UserInteraction.created_at.desc())
        .limit(50)
        .all()
    )
    liked_ids = [r[0] for r in recent]
    seen_ids = set(liked_ids)

    scored = ml_registry.hybrid_model.recommend(
        user_id=current_user.id, liked_product_ids=liked_ids, top_k=limit, exclude_seen=seen_ids
    )

    if not scored:
        # Cold-start fallback: brand-new user with zero history -> trending products
        return trending(limit=limit, db=db)

    products = {p.id: p for p in db.query(Product).filter(Product.id.in_([s.product_id for s in scored])).all()}
    items = [
        RecommendationItem(product=ProductOut.model_validate(products[s.product_id]), score=s.score, reason=s.reason)
        for s in scored if s.product_id in products
    ]
    response = RecommendationResponse(user_id=current_user.id, strategy="hybrid", items=items)
    cache_set(cache_key, response.model_dump(), ttl_seconds=300)
    return response


@router.get("/trending", response_model=RecommendationResponse)
def trending(limit: int = 10, db: Session = Depends(get_db)):
    """Popularity-ranked products — used for anonymous users and cold-start."""
    cache_key = f"reco:trending:{limit}"
    cached = cache_get(cache_key)
    if cached:
        return cached

    products = db.query(Product).order_by(Product.popularity_score.desc()).limit(limit).all()
    items = [
        RecommendationItem(product=ProductOut.model_validate(p), score=p.popularity_score, reason="Trending among all shoppers")
        for p in products
    ]
    response = RecommendationResponse(user_id=None, strategy="popularity", items=items)
    cache_set(cache_key, response.model_dump(), ttl_seconds=600)
    return response
