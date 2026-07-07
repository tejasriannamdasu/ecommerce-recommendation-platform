"""Product catalog endpoints: list/filter, search (keyword + semantic), details."""
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import Optional

from app.database import get_db
from app.models.product import Product
from app.models.interaction import UserInteraction, InteractionType
from app.schemas.product import ProductOut, ProductSearchResult
from app.auth.dependencies import get_current_user
from app.models.user import User
from app.ml_state import ml_registry
from app.utils.cache import cache_get, cache_set

router = APIRouter(prefix="/products", tags=["Products"])


@router.get("", response_model=list[ProductOut])
def get_products(
    category_id: Optional[int] = None,
    min_price: Optional[float] = None,
    max_price: Optional[float] = None,
    brand: Optional[str] = None,
    sort_by: str = Query("popularity", enum=["popularity", "price_asc", "price_desc", "rating"]),
    limit: int = 20,
    offset: int = 0,
    db: Session = Depends(get_db),
):
    q = db.query(Product)
    if category_id:
        q = q.filter(Product.category_id == category_id)
    if min_price is not None:
        q = q.filter(Product.price >= min_price)
    if max_price is not None:
        q = q.filter(Product.price <= max_price)
    if brand:
        q = q.filter(Product.brand.ilike(f"%{brand}%"))

    if sort_by == "price_asc":
        q = q.order_by(Product.price.asc())
    elif sort_by == "price_desc":
        q = q.order_by(Product.price.desc())
    elif sort_by == "rating":
        q = q.order_by(Product.avg_rating.desc())
    else:
        q = q.order_by(Product.popularity_score.desc())

    return q.offset(offset).limit(limit).all()


@router.get("/search", response_model=ProductSearchResult)
def search_products(q: str, semantic: bool = True, limit: int = 20, db: Session = Depends(get_db)):
    """
    Keyword search (SQL ILIKE) by default; set semantic=true to use the
    Sentence-Transformers + FAISS engine for meaning-based matches
    (e.g. 'wireless headphones for gaming' -> 'Bluetooth Gaming Headset').
    """
    cache_key = f"search:{semantic}:{q.lower()}:{limit}"
    cached = cache_get(cache_key)
    if cached:
        return cached

    if semantic and ml_registry.semantic_engine is not None:
        pairs = ml_registry.semantic_engine.search(q, top_k=limit)
        ids = [pid for pid, _ in pairs]
        products = db.query(Product).filter(Product.id.in_(ids)).all()
        order = {pid: i for i, pid in enumerate(ids)}
        products.sort(key=lambda p: order.get(p.id, 999))
    else:
        products = (
            db.query(Product)
            .filter(Product.title.ilike(f"%{q}%") | Product.description.ilike(f"%{q}%"))
            .limit(limit)
            .all()
        )

    result = ProductSearchResult(
        products=[ProductOut.model_validate(p) for p in products],
        total=len(products),
        query=q,
    )
    cache_set(cache_key, result.model_dump(), ttl_seconds=180)
    return result


@router.get("/autocomplete")
def autocomplete(prefix: str, limit: int = 8, db: Session = Depends(get_db)):
    """Search-as-you-type suggestions based on title prefix match."""
    titles = (
        db.query(Product.title)
        .filter(Product.title.ilike(f"{prefix}%"))
        .limit(limit)
        .all()
    )
    return {"suggestions": [t[0] for t in titles]}


@router.get("/{product_id}", response_model=ProductOut)
def get_product(product_id: int, db: Session = Depends(get_db)):
    product = db.query(Product).filter(Product.id == product_id).first()
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    return product


@router.post("/{product_id}/view")
def log_view(product_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    """Logs a view interaction — feeds 'Recently Viewed' and the collaborative model."""
    product = db.query(Product).filter(Product.id == product_id).first()
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    db.add(UserInteraction(user_id=current_user.id, product_id=product_id, interaction_type=InteractionType.VIEW))
    db.commit()
    return {"message": "view logged"}


@router.get("/{product_id}/similar")
def similar_products(product_id: int, limit: int = 10, db: Session = Depends(get_db)):
    """Content-based 'Similar Product Suggestions' for the product detail page."""
    if ml_registry.content_model is None:
        raise HTTPException(status_code=503, detail="Recommendation models not loaded yet")
    pairs = ml_registry.content_model.similar_to_product(product_id, top_k=limit)
    ids = [pid for pid, _ in pairs]
    scores = {pid: s for pid, s in pairs}
    products = db.query(Product).filter(Product.id.in_(ids)).all()
    products.sort(key=lambda p: -scores.get(p.id, 0))
    return [{"product": ProductOut.model_validate(p), "similarity": scores.get(p.id, 0)} for p in products]
