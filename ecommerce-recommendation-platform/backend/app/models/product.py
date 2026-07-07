"""Product catalog + category taxonomy."""
from sqlalchemy import Column, Integer, String, Text, Float, ForeignKey, DateTime
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.database import Base


class Category(Base):
    __tablename__ = "categories"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(150), unique=True, nullable=False)
    parent_id = Column(Integer, ForeignKey("categories.id"), nullable=True)

    products = relationship("Product", back_populates="category")


class Product(Base):
    __tablename__ = "products"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(500), nullable=False, index=True)
    description = Column(Text, nullable=True)
    tags = Column(String(500), nullable=True)  # comma-separated
    price = Column(Float, nullable=False, default=0.0)
    category_id = Column(Integer, ForeignKey("categories.id"), nullable=True)
    brand = Column(String(150), nullable=True)
    image_url = Column(String(500), nullable=True)
    avg_rating = Column(Float, default=0.0)
    num_ratings = Column(Integer, default=0)
    popularity_score = Column(Float, default=0.0)  # precomputed for cold-start ranking
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    category = relationship("Category", back_populates="products")
