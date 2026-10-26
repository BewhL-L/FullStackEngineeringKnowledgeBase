"""
缓存抽象（可选 Redis）
- 配置 REDIS_URL 且 redis 可用时使用 Redis（多进程/多实例共享）
- 否则降级为进程内内存字典
可用于热点问答缓存、通用 KV。
"""
import json
import hashlib
from typing import Optional

from ..config import settings
from ..utils.logger import get_logger

logger = get_logger(__name__)


class MemoryCache:
    def __init__(self):
        self._d = {}

    def get(self, key: str):
        return self._d.get(key)

    def set(self, key: str, value, ttl: int = None) -> None:
        self._d[key] = value


class RedisCache:
    def __init__(self, client):
        self.r = client

    def get(self, key: str):
        v = self.r.get(key)
        return json.loads(v) if v else None

    def set(self, key: str, value, ttl: int = None) -> None:
        data = json.dumps(value, ensure_ascii=False)
        if ttl:
            self.r.setex(key, ttl, data)
        else:
            self.r.set(key, data)


def build_cache():
    if settings.REDIS_URL:
        try:
            import redis

            client = redis.Redis.from_url(settings.REDIS_URL, socket_connect_timeout=2)
            client.ping()
            logger.info("缓存使用 Redis")
            return RedisCache(client)
        except Exception as e:
            logger.warning(f"Redis 不可用，降级为内存缓存：{e}")
    return MemoryCache()


cache = build_cache()


def cache_key(prefix: str, *parts) -> str:
    h = hashlib.md5("|".join(str(p) for p in parts).encode("utf-8")).hexdigest()
    return f"{prefix}:{h}"
