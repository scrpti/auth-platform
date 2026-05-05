import json
import functools
from app.core.limiter import redis_client

def cache(expire: int = 60):
    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            # Excluimos objetos no serializables como db de la clave
            safe_args = [a for a in args if isinstance(a, (str, int, float, bool))]
            safe_kwargs = {k: v for k, v in kwargs.items() if isinstance(v, (str, int, float, bool))}
            key = f"cache:{func.__name__}:{safe_args}:{safe_kwargs}"

            cached = redis_client.get(key)
            if cached:
                return json.loads(cached)

            result = func(*args, **kwargs)
            redis_client.setex(key, expire, json.dumps(result, default=str))
            return result
        return wrapper
    return decorator