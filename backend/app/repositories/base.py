"""
Repository基类
提供通用的数据访问方法，封装HTTP请求逻辑
"""
from typing import List, Optional, Dict, Any, TypeVar, Generic, Type
from abc import ABC, abstractmethod
import logging

from app.core.http_client import http_client
from app.models.base import BaseModel

logger = logging.getLogger(__name__)

T = TypeVar('T', bound=BaseModel)


class BaseRepository(Generic[T], ABC):
    """
    Repository基类
    封装通用的数据访问逻辑
    """
    
    def __init__(self, model_class: Type[T], table_name: str):
        """
        初始化Repository
        
        Args:
            model_class: 对应的模型类
            table_name: 数据库表名
        """
        self.model_class = model_class
        self.table_name = table_name
        self.client = http_client
    
    async def find_all(
        self, 
        filters: Optional[Dict[str, Any]] = None,
        limit: int = 100,
        offset: int = 0,
        order_by: Optional[str] = None
    ) -> List[T]:
        """查询所有记录"""
        try:
            # 默认过滤已删除的记录
            if filters is None:
                filters = {}
            filters.setdefault("is_deleted", False)
            
            result = await self.client.query_table(
                table_name=self.table_name,
                filters=filters,
                limit=limit,
                offset=offset,
                order_by=order_by
            )
            
            records = result.get("data", {}).get("records", [])
            return self.model_class.from_list(records)
            
        except Exception as e:
            logger.error(f"查询{self.table_name}失败: {e}")
            return []
    
    async def find_by_id(self, entity_id: str) -> Optional[T]:
        """根据ID查询单条记录"""
        try:
            result = await self.client.query_table(
                table_name=self.table_name,
                filters={
                    self._get_primary_key_field(): entity_id,
                    "is_deleted": False
                },
                limit=1
            )
            
            records = result.get("data", {}).get("records", [])
            if records:
                return self.model_class.from_dict(records[0])
            return None
            
        except Exception as e:
            logger.error(f"根据ID查询{self.table_name}失败: {e}")
            return None
    
    async def find_by_filters(
        self, 
        filters: Dict[str, Any],
        limit: int = 100,
        offset: int = 0,
        order_by: Optional[str] = None
    ) -> List[T]:
        """根据条件查询"""
        # 默认过滤已删除的记录
        filters.setdefault("is_deleted", False)
        return await self.find_all(filters, limit, offset, order_by)
    
    async def find_one_by_filters(self, filters: Dict[str, Any]) -> Optional[T]:
        """根据条件查询单条记录"""
        results = await self.find_by_filters(filters, limit=1)
        return results[0] if results else None
    
    async def count(self, filters: Optional[Dict[str, Any]] = None) -> int:
        """计数"""
        try:
            if filters is None:
                filters = {}
            filters.setdefault("is_deleted", False)
            
            result = await self.client.query_table(
                table_name=self.table_name,
                filters=filters,
                limit=1
            )
            
            return result.get("data", {}).get("estimated_total", 0)
            
        except Exception as e:
            logger.error(f"计数{self.table_name}失败: {e}")
            return 0
    
    async def exists(self, filters: Dict[str, Any]) -> bool:
        """检查记录是否存在"""
        count = await self.count(filters)
        return count > 0
    
    async def join_query(
        self,
        join_table: str,
        join_condition: str,
        filters: Optional[Dict[str, Any]] = None,
        limit: int = 100,
        offset: int = 0
    ) -> List[T]:
        """关联查询"""
        try:
            if filters is None:
                filters = {}
            
            result = await self.client.join_query(
                main_table=self.table_name,
                join_table=join_table,
                join_condition=join_condition,
                filters=filters,
                limit=limit,
                offset=offset
            )
            
            records = result.get("records", [])
            return self.model_class.from_list(records)
            
        except Exception as e:
            logger.error(f"关联查询{self.table_name}失败: {e}")
            return []
    
    async def get_statistics(
        self,
        field: str,
        operation: str = "count",
        group_by: Optional[str] = None,
        filters: Optional[Dict[str, Any]] = None
    ) -> Any:
        """获取统计信息"""
        try:
            if filters is None:
                filters = {}
            filters.setdefault("is_deleted", False)
            
            return await self.client.get_statistics(
                table_name=self.table_name,
                field=field,
                operation=operation,
                group_by=group_by,
                filters=filters
            )
            
        except Exception as e:
            logger.error(f"统计{self.table_name}失败: {e}")
            return 0
    
    @abstractmethod
    def _get_primary_key_field(self) -> str:
        """获取主键字段名，子类必须实现"""
        pass
    
    def _apply_default_filters(self, filters: Dict[str, Any]) -> Dict[str, Any]:
        """应用默认过滤条件"""
        filters.setdefault("is_deleted", False)
        return filters
    
    def _log_operation(self, operation: str, **kwargs):
        """记录操作日志"""
        logger.info(f"{operation} {self.table_name}: {kwargs}")
    
    async def _enrich_with_related_data(self, records: List[T]) -> List[T]:
        """
        使用关联数据丰富记录
        子类可以重写此方法来添加关联数据
        """
        return records 