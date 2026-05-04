from slowapi import Limiter
from slowapi.util import get_remote_address
import redis
from app.core.config import settings

redis_client = redis.from_url(settings.REDIS_URL)
limiter = Limiter(
    key_func=get_remote_address,
    storage_uri=settings.REDIS_URL
)