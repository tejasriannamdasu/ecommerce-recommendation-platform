from pydantic import BaseModel
from typing import Optional, List


class ProductOut(BaseModel):
    id: int
    title: str
    description: Optional[str] = None
    tags: Optional[str] = None
    price: float
    brand: Optional[str] = None
    image_url: Optional[str] = None
    avg_rating: float
    num_ratings: int
    category_id: Optional[int] = None

    class Config:
        from_attributes = True


class ProductSearchResult(BaseModel):
    products: List[ProductOut]
    total: int
    query: str


class RecommendationItem(BaseModel):
    product: ProductOut
    score: float
    reason: str  # human-readable explanation, e.g. "Because you liked X"


class RecommendationResponse(BaseModel):
    user_id: Optional[int]
    strategy: str
    items: List[RecommendationItem]
