"""Wishlist + recently-viewed + user profile endpoints."""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.wishlist import Wishlist
from app.models.product import Product
from app.models.interaction import UserInteraction, InteractionType
from app.schemas.product import ProductOut
from app.schemas.auth import UserOut
from app.auth.dependencies import get_current_user
from app.models.user import User

router = APIRouter(tags=["Wishlist & Profile"])


@router.post("/wishlist/{product_id}")
def add_to_wishlist(product_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    if not db.query(Product).filter(Product.id == product_id).first():
        raise HTTPException(status_code=404, detail="Product not found")
    exists = db.query(Wishlist).filter_by(user_id=current_user.id, product_id=product_id).first()
    if not exists:
        db.add(Wishlist(user_id=current_user.id, product_id=product_id))
        db.add(UserInteraction(user_id=current_user.id, product_id=product_id, interaction_type=InteractionType.WISHLIST))
        db.commit()
    return {"message": "added to wishlist"}


@router.delete("/wishlist/{product_id}")
def remove_from_wishlist(product_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    db.query(Wishlist).filter_by(user_id=current_user.id, product_id=product_id).delete()
    db.commit()
    return {"message": "removed from wishlist"}


@router.get("/wishlist", response_model=list[ProductOut])
def get_wishlist(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    product_ids = [w.product_id for w in db.query(Wishlist).filter_by(user_id=current_user.id).all()]
    return db.query(Product).filter(Product.id.in_(product_ids)).all()


@router.get("/recently-viewed", response_model=list[ProductOut])
def recently_viewed(limit: int = 10, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    interactions = (
        db.query(UserInteraction)
        .filter(UserInteraction.user_id == current_user.id, UserInteraction.interaction_type == InteractionType.VIEW)
        .order_by(UserInteraction.created_at.desc())
        .limit(limit)
        .all()
    )
    ids = [i.product_id for i in interactions]
    products = {p.id: p for p in db.query(Product).filter(Product.id.in_(ids)).all()}
    return [products[i] for i in ids if i in products]


@router.get("/profile", response_model=UserOut)
def profile(current_user: User = Depends(get_current_user)):
    return current_user
