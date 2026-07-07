"""
Centralized application configuration using pydantic-settings.
All values are overridable via environment variables / .env file,
which keeps secrets out of source control (12-factor app principle).
"""
from pydantic_settings import BaseSettings
from functools import lru_cache


class Settings(BaseSettings):
    # App
    APP_NAME: str = "AI-Powered E-Commerce Recommendation Platform"
    ENV: str = "development"
    API_V1_PREFIX: str = "/api/v1"

    # Database
    DATABASE_URL: str = "postgresql+psycopg2://postgres:postgres@db:5432/ecommerce_reco"

    # Redis (caching + rate limiting)
    REDIS_URL: str = "redis://redis:6379/0"

    # JWT Auth
    JWT_SECRET_KEY: str = "CHANGE_ME_IN_PRODUCTION_USE_ENV_VAR"
    JWT_ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24  # 24h

    # ML
    ML_MODELS_DIR: str = "/app/ml_models"
    SEMANTIC_MODEL_NAME: str = "all-MiniLM-L6-v2"
    CONTENT_WEIGHT: float = 0.5      # hybrid blend weight
    COLLAB_WEIGHT: float = 0.5

    # Rate limiting
    RATE_LIMIT_DEFAULT: str = "100/minute"

    class Config:
        env_file = ".env"
        case_sensitive = True


@lru_cache
def get_settings() -> Settings:
    return Settings()
