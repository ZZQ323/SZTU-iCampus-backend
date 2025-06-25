"""
内存缓存管理器
实现TTL和LRU策略的高性能内存缓存
"""
import time
import asyncio
import threading
from typing import Any, Dict, Optional, Set
from collections import OrderedDict
import logging
import hashlib
import json

logger = logging.getLogger(__name__)


class MemoryCache:
    """
    内存缓存管理器
    支持TTL（生存时间）和LRU（最近最少使用）策略
    """
    
    def __init__(self, max_size: int = 1000, default_ttl: int = 300):
        """
        初始化缓存管理器
        
        Args:
            max_size: 最大缓存条目数
            default_ttl: 默认TTL时间（秒）
        """
        self.max_size = max_size
        self.default_ttl = default_ttl
        self._cache: OrderedDict = OrderedDict()
        self._timestamps: Dict[str, float] = {}
        self._lock = threading.RLock()
        self._stats = {
            "hits": 0,
            "misses": 0,
            "evictions": 0,
            "expired": 0
        }
    
    def _generate_key(self, prefix: str, **kwargs) -> str:
        """生成缓存键"""
        # 将参数转换为稳定的字符串表示
        params_str = json.dumps(kwargs, sort_keys=True, default=str)
        key_data = f"{prefix}:{params_str}"
        return hashlib.md5(key_data.encode()).hexdigest()[:16]
    
    def get(self, key: str) -> Optional[Any]:
        """获取缓存数据"""
        with self._lock:
            current_time = time.time()
            
            if key not in self._cache:
                self._stats["misses"] += 1
                return None
            
            # 检查是否过期
            if key in self._timestamps:
                if current_time - self._timestamps[key] > self.default_ttl:
                    del self._cache[key]
                    del self._timestamps[key]
                    self._stats["expired"] += 1
                    self._stats["misses"] += 1
                    return None
            
            # 移动到末尾（LRU）
            value = self._cache.pop(key)
            self._cache[key] = value
            self._stats["hits"] += 1
            
            return value
    
    def set(self, key: str, value: Any, ttl: Optional[int] = None) -> None:
        """设置缓存数据"""
        with self._lock:
            current_time = time.time()
            
            # 如果键已存在，先删除旧记录
            if key in self._cache:
                del self._cache[key]
                if key in self._timestamps:
                    del self._timestamps[key]
            
            # 检查容量限制
            while len(self._cache) >= self.max_size:
                # 删除最旧的条目
                oldest_key = next(iter(self._cache))
                del self._cache[oldest_key]
                if oldest_key in self._timestamps:
                    del self._timestamps[oldest_key]
                self._stats["evictions"] += 1
            
            # 添加新条目
            self._cache[key] = value
            self._timestamps[key] = current_time
    
    def delete(self, key: str) -> bool:
        """删除缓存条目"""
        with self._lock:
            if key in self._cache:
                del self._cache[key]
                if key in self._timestamps:
                    del self._timestamps[key]
                return True
            return False
    
    def clear(self) -> None:
        """清空所有缓存"""
        with self._lock:
            self._cache.clear()
            self._timestamps.clear()
    
    def get_stats(self) -> Dict[str, Any]:
        """获取缓存统计信息"""
        with self._lock:
            total_requests = self._stats["hits"] + self._stats["misses"]
            hit_rate = self._stats["hits"] / total_requests if total_requests > 0 else 0
            
            return {
                "size": len(self._cache),
                "max_size": self.max_size,
                "hits": self._stats["hits"],
                "misses": self._stats["misses"],
                "hit_rate": f"{hit_rate:.2%}",
                "evictions": self._stats["evictions"],
                "expired": self._stats["expired"]
            }
    
    def cleanup_expired(self) -> int:
        """清理过期条目"""
        with self._lock:
            current_time = time.time()
            expired_keys = []
            
            for key, timestamp in self._timestamps.items():
                if current_time - timestamp > self.default_ttl:
                    expired_keys.append(key)
            
            for key in expired_keys:
                del self._cache[key]
                del self._timestamps[key]
                self._stats["expired"] += 1
            
            return len(expired_keys)


class CacheManager:
    """
    缓存管理器 - 为不同类型的数据提供专门的缓存实例
    """
    
    def __init__(self):
        # 不同类型数据使用不同的缓存配置
        self.user_cache = MemoryCache(max_size=500, default_ttl=600)      # 用户信息，10分钟
        self.course_cache = MemoryCache(max_size=1000, default_ttl=1800)  # 课程信息，30分钟
        self.schedule_cache = MemoryCache(max_size=300, default_ttl=300)  # 课表信息，5分钟
        self.general_cache = MemoryCache(max_size=500, default_ttl=300)   # 通用缓存，5分钟
        
        # 启动定期清理任务
        self._start_cleanup_task()
    
    def _start_cleanup_task(self):
        """启动定期清理过期缓存的任务"""
        def cleanup_worker():
            while True:
                try:
                    time.sleep(60)  # 每分钟清理一次
                    total_cleaned = 0
                    total_cleaned += self.user_cache.cleanup_expired()
                    total_cleaned += self.course_cache.cleanup_expired()
                    total_cleaned += self.schedule_cache.cleanup_expired()
                    total_cleaned += self.general_cache.cleanup_expired()
                    
                    if total_cleaned > 0:
                        logger.info(f"缓存清理完成，删除 {total_cleaned} 个过期条目")
                        
                except Exception as e:
                    logger.error(f"缓存清理任务异常: {e}")
        
        cleanup_thread = threading.Thread(target=cleanup_worker, daemon=True)
        cleanup_thread.start()
    
    # === 用户信息缓存 ===
    def get_user(self, person_id: str) -> Optional[Dict]:
        """获取用户信息缓存"""
        key = self.user_cache._generate_key("user", person_id=person_id)
        return self.user_cache.get(key)
    
    def set_user(self, person_id: str, user_data: Dict) -> None:
        """设置用户信息缓存"""
        key = self.user_cache._generate_key("user", person_id=person_id)
        self.user_cache.set(key, user_data)
    
    # === 课程信息缓存 ===
    def get_course(self, course_id: str) -> Optional[Dict]:
        """获取课程信息缓存"""
        key = self.course_cache._generate_key("course", course_id=course_id)
        return self.course_cache.get(key)
    
    def set_course(self, course_id: str, course_data: Dict) -> None:
        """设置课程信息缓存"""
        key = self.course_cache._generate_key("course", course_id=course_id)
        self.course_cache.set(key, course_data)
    
    def get_course_instance(self, instance_id: str) -> Optional[Dict]:
        """获取课程实例缓存"""
        key = self.course_cache._generate_key("instance", instance_id=instance_id)
        return self.course_cache.get(key)
    
    def set_course_instance(self, instance_id: str, instance_data: Dict) -> None:
        """设置课程实例缓存"""
        key = self.course_cache._generate_key("instance", instance_id=instance_id)
        self.course_cache.set(key, instance_data)
    
    # === 课表信息缓存 ===
    def get_student_schedule(self, student_id: str, semester: Optional[str] = None) -> Optional[Dict]:
        """获取学生课表缓存"""
        key = self.schedule_cache._generate_key("schedule", student_id=student_id, semester=semester)
        return self.schedule_cache.get(key)
    
    def set_student_schedule(self, student_id: str, schedule_data: Dict, semester: Optional[str] = None) -> None:
        """设置学生课表缓存"""
        key = self.schedule_cache._generate_key("schedule", student_id=student_id, semester=semester)
        self.schedule_cache.set(key, schedule_data)
    
    # === 通用查询缓存 ===
    def get_query_result(self, table_name: str, **filters) -> Optional[Dict]:
        """获取通用查询结果缓存"""
        key = self.general_cache._generate_key(f"query_{table_name}", **filters)
        return self.general_cache.get(key)
    
    def set_query_result(self, table_name: str, result_data: Dict, **filters) -> None:
        """设置通用查询结果缓存"""
        key = self.general_cache._generate_key(f"query_{table_name}", **filters)
        self.general_cache.set(key, result_data)
    
    def invalidate_user(self, person_id: str) -> None:
        """失效用户相关缓存"""
        user_key = self.user_cache._generate_key("user", person_id=person_id)
        self.user_cache.delete(user_key)
        
        # 如果是学生，同时失效课表缓存
        if person_id.startswith('P'):
            student_id = person_id.replace('P', '')
            schedule_key = self.schedule_cache._generate_key("schedule", student_id=student_id, semester=None)
            self.schedule_cache.delete(schedule_key)
    
    def get_all_stats(self) -> Dict[str, Any]:
        """获取所有缓存的统计信息"""
        return {
            "user_cache": self.user_cache.get_stats(),
            "course_cache": self.course_cache.get_stats(),
            "schedule_cache": self.schedule_cache.get_stats(),
            "general_cache": self.general_cache.get_stats()
        }


# 全局缓存管理器实例
cache_manager = CacheManager() 