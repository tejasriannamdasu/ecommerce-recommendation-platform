"""
Application entry point. Wires together routers, middleware
(CORS, rate limiting), and loads trained ML models into memory
on startup.
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from slowapi.errors import RateLimitExceeded
from slowapi import _rate_limit_exceeded_handler

from app.config import get_settings
from app.database import Base, engine
from app.utils.rate_limiter import limiter
from app.ml_state import ml_registry
from app.routers import auth, products, recommendations, analytics, wishlist

settings = get_settings()

app = FastAPI(
    title=settings.APP_NAME,
    description="Full-stack recommendation platform: content-based, collaborative "
                 "filtering, hybrid ranking, and semantic (vector) search.",
    version="1.0.0",
)

app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"] if settings.ENV == "development" else [],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.on_event("startup")
def on_startup():
    Base.metadata.create_all(bind=engine)  # dev convenience; use Alembic migrations in prod
    ml_registry.load()


@app.get("/health", tags=["System"])
def health_check():
    return {
        "status": "ok",
        "models_loaded": ml_registry.hybrid_model is not None,
        "semantic_mode": ml_registry.semantic_engine.mode if ml_registry.semantic_engine else None,
    }


app.include_router(auth.router, prefix=settings.API_V1_PREFIX)
app.include_router(products.router, prefix=settings.API_V1_PREFIX)
app.include_router(recommendations.router, prefix=settings.API_V1_PREFIX)
app.include_router(analytics.router, prefix=settings.API_V1_PREFIX)
app.include_router(wishlist.router, prefix=settings.API_V1_PREFIX)
