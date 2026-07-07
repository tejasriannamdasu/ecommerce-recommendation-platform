"""
Thin Redis caching wrapper. Recommendation results are relatively
expensive to compute (vector search + model inference) so we cache
per-user results for a short TTL. Falls back to a no-op in-memory
dict if Redis is unreachable, so local dev without Redis still works.
"""
import json
import redis
from app.config import get_settings

settings = get_settings()

try:
    _client = redis.from_url(settings.REDIS_URL, decode_responses=True, socket_connect_timeout=1)
    _client.ping()
    REDIS_AVAILABLE = True
except Exception:
    _client = None
    REDIS_AVAILABLE = False

_fallback_store: dict = {}


def cache_get(key: str):
    if REDIS_AVAILABLE:
        val = _client.get(key)
        return json.loads(val) if val else None
    return _fallback_store.get(key)


def cache_set(key: str, value, ttl_seconds: int = 300):
    if REDIS_AVAILABLE:
        _client.setex(key, ttl_seconds, json.dumps(value))
    else:
        _fallback_store[key] = value


def cache_invalidate(prefix: str):
    if REDIS_AVAILABLE:
        for k in _client.scan_iter(f"{prefix}*"):
            _client.delete(k)
    else:
        for k in list(_fallback_store):
            if k.startswith(prefix):
                del _fallback_store[k]
