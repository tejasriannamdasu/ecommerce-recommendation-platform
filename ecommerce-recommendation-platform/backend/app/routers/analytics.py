"""Admin analytics dashboard endpoints (role-protected)."""
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import func

from app.database import get_db
from app.models.product import Product, Category
from app.models.interaction import UserInteraction, InteractionType
from app.models.order import Order, OrderItem
from app.auth.dependencies import require_role

router = APIRouter(prefix="/analytics", tags=["Analytics"], dependencies=[Depends(require_role("admin"))])


@router.get("/dashboard")
def dashboard_metrics(db: Session = Depends(get_db)):
    most_viewed = (
        db.query(Product.title, func.count(UserInteraction.id).label("views"))
        .join(UserInteraction, UserInteraction.product_id == Product.id)
        .filter(UserInteraction.interaction_type == InteractionType.VIEW)
        .group_by(Product.id)
        .order_by(func.count(UserInteraction.id).desc())
        .limit(10)
        .all()
    )

    most_purchased = (
        db.query(Product.title, func.sum(OrderItem.quantity).label("units_sold"))
        .join(OrderItem, OrderItem.product_id == Product.id)
        .group_by(Product.id)
        .order_by(func.sum(OrderItem.quantity).desc())
        .limit(10)
        .all()
    )

    top_categories = (
        db.query(Category.name, func.count(Product.id).label("num_products"))
        .join(Product, Product.category_id == Category.id)
        .group_by(Category.id)
        .order_by(func.count(Product.id).desc())
        .limit(10)
        .all()
    )

    total_users = db.query(func.count(func.distinct(UserInteraction.user_id))).scalar() or 0
    total_orders = db.query(func.count(Order.id)).scalar() or 0
    total_revenue = db.query(func.coalesce(func.sum(Order.total_amount), 0)).scalar() or 0

    return {
        "most_viewed_products": [{"title": t, "views": v} for t, v in most_viewed],
        "most_purchased_products": [{"title": t, "units_sold": int(u or 0)} for t, u in most_purchased],
        "top_categories": [{"category": c, "num_products": n} for c, n in top_categories],
        "user_activity": {"active_users": total_users, "total_orders": total_orders, "total_revenue": float(total_revenue)},
        "recommendation_engine_status": "See /api/v1/recommendations for live strategy in use",
    }
