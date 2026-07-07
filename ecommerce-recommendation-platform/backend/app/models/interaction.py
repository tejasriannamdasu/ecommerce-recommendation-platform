"""
Implicit + explicit feedback signals that feed the collaborative
filtering model: views, clicks, purchases, and star ratings.
"""
import enum
from sqlalchemy import Column, Integer, Float, ForeignKey, DateTime, Enum
from sqlalchemy.sql import func
from app.database import Base


class InteractionType(str, enum.Enum):
    VIEW = "view"
    CLICK = "click"
    PURCHASE = "purchase"
    WISHLIST = "wishlist"


class UserInteraction(Base):
    __tablename__ = "user_interactions"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    product_id = Column(Integer, ForeignKey("products.id"), nullable=False, index=True)
    interaction_type = Column(Enum(InteractionType), nullable=False)
    weight = Column(Float, default=1.0)  # e.g. view=1, click=2, purchase=5
    created_at = Column(DateTime(timezone=True), server_default=func.now())


class Rating(Base):
    __tablename__ = "ratings"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    product_id = Column(Integer, ForeignKey("products.id"), nullable=False, index=True)
    score = Column(Float, nullable=False)  # 1-5
    created_at = Column(DateTime(timezone=True), server_default=func.now())
