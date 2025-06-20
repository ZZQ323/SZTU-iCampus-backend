"""
数据服务客户端
实现与独立数据服务的集成，支持配置开关切换Mock/Real数据
"""
import asyncio
import json
import time
from typing import Dict, List, Optional, Any, AsyncGenerator
from datetime import datetime

import httpx
import redis.asyncio as redis
from loguru import logger

from .config import settings, DATA_SERVICE_PATHS, CACHE_KEYS


class DataServiceClient:
    """数据服务客户端"""
    
    def __init__(self):
        self.base_url = settings.DATA_SERVICE_URL
        self.api_key = settings.DATA_SERVICE_API_KEY
        self.timeout = settings.DATA_SERVICE_TIMEOUT
        self.headers = {
            "X-API-Key": self.api_key,
            "Content-Type": "application/json"
        }
        
        # Redis缓存客户端
        self.redis_client = None
        
    async def init_redis(self):
        """初始化Redis连接"""
        try:
            self.redis_client = redis.from_url(settings.REDIS_URL)
            await self.redis_client.ping()
            logger.info("Redis连接成功")
        except Exception as e:
            logger.warning(f"Redis连接失败: {e}，将不使用缓存")
            self.redis_client = None
    
    async def close_redis(self):
        """关闭Redis连接"""
        if self.redis_client:
            await self.redis_client.close()
    
    async def get_cache(self, key: str) -> Optional[Dict]:
        """获取缓存数据"""
        if not self.redis_client:
            return None
        
        try:
            cached_data = await self.redis_client.get(key)
            if cached_data:
                data = json.loads(cached_data)
                logger.debug(f"缓存命中: {key}")
                return data
        except Exception as e:
            logger.error(f"获取缓存失败: {e}")
        
        return None
    
    async def set_cache(self, key: str, data: Dict, expire: int = None):
        """设置缓存数据"""
        if not self.redis_client:
            return
        
        try:
            expire = expire or settings.CACHE_EXPIRE_SECONDS
            await self.redis_client.setex(
                key, 
                expire, 
                json.dumps(data, ensure_ascii=False, default=str)
            )
            logger.debug(f"缓存设置成功: {key}")
        except Exception as e:
            logger.error(f"设置缓存失败: {e}")
    
    async def delete_cache(self, pattern: str):
        """删除缓存（支持模式匹配）"""
        if not self.redis_client:
            return
        
        try:
            keys = await self.redis_client.keys(pattern)
            if keys:
                await self.redis_client.delete(*keys)
                logger.info(f"删除缓存: {len(keys)}个key")
        except Exception as e:
            logger.error(f"删除缓存失败: {e}")
    
    async def request(self, method: str, path: str, **kwargs) -> Dict:
        """发送HTTP请求到数据服务"""
        if not settings.DATA_SERVICE_ENABLED:
            logger.warning("数据服务已禁用，返回Mock数据")
            return await self._get_mock_data(path)
        
        url = f"{self.base_url}{path}"
        
        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.request(
                    method=method,
                    url=url,
                    headers=self.headers,
                    **kwargs
                )
                response.raise_for_status()
                return response.json()
                
        except httpx.TimeoutException:
            logger.error(f"数据服务请求超时: {url}")
            return {"success": False, "message": "请求超时"}
        except httpx.HTTPStatusError as e:
            logger.error(f"数据服务HTTP错误: {e.response.status_code} - {url}")
            return {"success": False, "message": f"HTTP {e.response.status_code}"}
        except Exception as e:
            logger.error(f"数据服务请求失败: {url} - {e}")
            return {"success": False, "message": "服务不可用"}
    
    async def _get_mock_data(self, path: str) -> Dict:
        """获取Mock数据"""
        # 这里可以返回预定义的Mock数据
        # 实际项目中可以从本地文件或内存中加载
        mock_data = {
            "/health": {"status": "ok", "service": "mock"},
            "/stats": {"total_users": 1000, "active_courses": 50},
            "/persons": {
                "success": True,
                "data": [
                    {"id": 1, "name": "张三", "role": "student"},
                    {"id": 2, "name": "李四", "role": "teacher"}
                ],
                "total": 2
            }
        }
        
        return mock_data.get(path, {"success": False, "message": "Mock数据未找到"})
    
    # === 业务API方法 ===
    
    async def get_health(self) -> Dict:
        """获取服务健康状态"""
        cache_key = "health_status"
        cached = await self.get_cache(cache_key)
        if cached:
            return cached
        
        result = await self.request("GET", DATA_SERVICE_PATHS["health"])
        
        if result.get("success", True):  # 健康检查缓存时间短一些
            await self.set_cache(cache_key, result, expire=30)
        
        return result
    
    async def get_stats(self) -> Dict:
        """获取统计数据"""
        cache_key = CACHE_KEYS["stats"]
        cached = await self.get_cache(cache_key)
        if cached:
            return cached
        
        result = await self.request("GET", DATA_SERVICE_PATHS["stats"])
        
        if result.get("success", True):
            await self.set_cache(cache_key, result)
        
        return result
    
    async def get_persons(
        self, 
        role: Optional[str] = None,
        page: int = 1,
        limit: int = 20,
        search: Optional[str] = None
    ) -> Dict:
        """获取人员列表"""
        params = {"page": page, "limit": limit}
        if role:
            params["role"] = role
        if search:
            params["search"] = search
        
        # 生成缓存键
        cache_key = f"persons:{role or 'all'}:{page}:{limit}:{search or 'all'}"
        cached = await self.get_cache(cache_key)
        if cached:
            return cached
        
        result = await self.request(
            "GET", 
            DATA_SERVICE_PATHS["persons"],
            params=params
        )
        
        if result.get("success", True):
            await self.set_cache(cache_key, result)
        
        return result
    
    async def get_courses(
        self,
        semester: Optional[str] = None,
        teacher_id: Optional[int] = None,
        page: int = 1,
        limit: int = 20
    ) -> Dict:
        """获取课程列表"""
        params = {"page": page, "limit": limit}
        if semester:
            params["semester"] = semester
        if teacher_id:
            params["teacher_id"] = teacher_id
        
        cache_key = f"courses:{semester or 'all'}:{teacher_id or 'all'}:{page}:{limit}"
        cached = await self.get_cache(cache_key)
        if cached:
            return cached
        
        result = await self.request(
            "GET",
            DATA_SERVICE_PATHS["courses"], 
            params=params
        )
        
        if result.get("success", True):
            await self.set_cache(cache_key, result)
        
        return result
    
    async def get_user_schedule(self, user_id: int, semester: str) -> Dict:
        """获取用户课表"""
        cache_key = CACHE_KEYS["course_schedule"].format(
            user_id=user_id, 
            semester=semester
        )
        cached = await self.get_cache(cache_key)
        if cached:
            return cached
        
        result = await self.request(
            "GET",
            f"/persons/{user_id}/schedule",
            params={"semester": semester}
        )
        
        if result.get("success", True):
            await self.set_cache(cache_key, result, expire=3600)  # 课表缓存1小时
        
        return result
    
    async def get_announcements(
        self,
        page: int = 1,
        limit: int = 10,
        category: Optional[str] = None
    ) -> Dict:
        """获取公告列表"""
        cache_key = CACHE_KEYS["announcements"].format(page=page)
        if category:
            cache_key += f":{category}"
        
        cached = await self.get_cache(cache_key)
        if cached:
            return cached
        
        params = {"page": page, "limit": limit}
        if category:
            params["category"] = category
        
        result = await self.request(
            "GET",
            DATA_SERVICE_PATHS["announcements"],
            params=params
        )
        
        if result.get("success", True):
            await self.set_cache(cache_key, result, expire=600)  # 公告缓存10分钟
        
        return result
    
    async def stream_notifications(self) -> AsyncGenerator[str, None]:
        """流式获取通知推送"""
        if not settings.SSE_ENABLED:
            logger.warning("SSE推送已禁用")
            return
        
        url = f"{self.base_url}{DATA_SERVICE_PATHS['stream_notifications']}"
        
        try:
            async with httpx.AsyncClient(timeout=None) as client:
                async with client.stream(
                    "GET", 
                    url, 
                    headers=self.headers
                ) as response:
                    if response.status_code == 200:
                        async for line in response.aiter_lines():
                            if line.startswith("data:"):
                                yield line
                    else:
                        logger.error(f"SSE连接失败: {response.status_code}")
        except Exception as e:
            logger.error(f"SSE推送异常: {e}")
    
    async def invalidate_user_cache(self, user_id: int):
        """清除用户相关缓存"""
        patterns = [
            CACHE_KEYS["user_info"].format(user_id=user_id),
            f"schedule:{user_id}:*",
            f"library:{user_id}",
            f"grades:{user_id}:*"
        ]
        
        for pattern in patterns:
            await self.delete_cache(pattern)
        
        logger.info(f"用户 {user_id} 缓存已清理")


# 全局数据服务客户端实例
data_service = DataServiceClient()


async def init_data_service():
    """初始化数据服务客户端"""
    await data_service.init_redis()
    logger.info("数据服务客户端初始化完成")


async def close_data_service():
    """关闭数据服务客户端"""
    await data_service.close_redis()
    logger.info("数据服务客户端已关闭") 