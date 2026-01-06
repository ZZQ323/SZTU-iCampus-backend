import redis.asyncio as redis
from typing import Optional, Any
import json
from src.config import settings


class RedisClient:
    def __init__(self):
        self.redis: Optional[redis.Redis] = None

    async def connect(self):
        """连接到Redis"""
        self.redis = await redis.from_url(
            settings.REDIS_URL,
            password=settings.REDIS_PASSWORD,
            db=settings.REDIS_DB,
            encoding="utf-8",
            decode_responses=True,
            max_connections=settings.REDIS_POOL_SIZE,
        )

    async def disconnect(self):
        """断开Redis连接"""
        if self.redis:
            await self.redis.close()

    async def get(self, key: str) -> Optional[Any]:
        """获取值"""
        if not self.redis:
            return None
        value = await self.redis.get(key)
        if value:
            try:
                return json.loads(value)
            except json.JSONDecodeError:
                return value
        return None

    async def set(self, key: str, value: Any, expire: Optional[int] = None) -> bool:
        """设置值"""
        if not self.redis:
            return False
        if isinstance(value, (dict, list)):
            value = json.dumps(value)
        return await self.redis.set(key, value, ex=expire)

    async def delete(self, key: str) -> bool:
        """删除键"""
        if not self.redis:
            return False
        return await self.redis.delete(key) > 0

    async def exists(self, key: str) -> bool:
        """检查键是否存在"""
        if not self.redis:
            return False
        return await self.redis.exists(key) > 0

    async def get_session(self, session_id: str) -> Optional[dict]:
        """获取会话数据"""
        return await self.get(f"session:{session_id}")

    async def set_session(self, session_id: str, data: dict, expire: Optional[int] = None) -> bool:
        """设置会话数据"""
        if expire is None:
            expire = settings.SESSION_EXPIRE_SECONDS
        return await self.set(f"session:{session_id}", data, expire)

    async def delete_session(self, session_id: str) -> bool:
        """删除会话"""
        return await self.delete(f"session:{session_id}")


# 全局Redis客户端实例
redis_client = RedisClient()