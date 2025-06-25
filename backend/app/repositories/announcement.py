"""
公告Repository
处理公告相关的数据访问逻辑
"""
from typing import Optional, List, Dict, Any
from datetime import datetime
import logging

from .base import BaseRepository
from app.models.campus import Announcement

logger = logging.getLogger(__name__)


class AnnouncementRepository(BaseRepository[Announcement]):
    """公告Repository"""
    
    def __init__(self):
        super().__init__(Announcement, "announcements")
    
    def _get_primary_key_field(self) -> str:
        return "announcement_id"
    
    async def find_public_announcements(
        self,
        category: Optional[str] = None,
        priority: Optional[str] = None,
        limit: int = 20,
        offset: int = 0
    ) -> List[Announcement]:
        """查询公开公告"""
        try:
            filters = {
                "status": "published",
                "review_status": "approved"
            }
            
            # 只显示有效的公告
            now = datetime.now()
            filters["$or"] = [
                {"effective_date": {"$lte": now}, "expire_date": {"$gte": now}},
                {"effective_date": None, "expire_date": None},
                {"effective_date": {"$lte": now}, "expire_date": None},
                {"effective_date": None, "expire_date": {"$gte": now}}
            ]
            
            if category:
                filters["category"] = category
            
            if priority:
                filters["priority"] = priority
            
            return await self.find_by_filters(
                filters=filters,
                limit=limit,
                offset=offset,
                order_by="is_pinned DESC, is_urgent DESC, publish_time DESC"
            )
            
        except Exception as e:
            logger.error(f"查询公开公告失败: {e}")
            return []
    
    async def find_by_category(self, category: str, limit: int = 50) -> List[Announcement]:
        """根据类别查询公告"""
        try:
            return await self.find_by_filters(
                filters={
                    "category": category,
                    "status": "published",
                    "review_status": "approved"
                },
                limit=limit,
                order_by="publish_time DESC"
            )
        except Exception as e:
            logger.error(f"根据类别查询公告失败: {e}")
            return []
    
    async def find_urgent_announcements(self, limit: int = 10) -> List[Announcement]:
        """查询紧急公告"""
        try:
            return await self.find_by_filters(
                filters={
                    "is_urgent": True,
                    "status": "published",
                    "review_status": "approved"
                },
                limit=limit,
                order_by="publish_time DESC"
            )
        except Exception as e:
            logger.error(f"查询紧急公告失败: {e}")
            return []
    
    async def find_pinned_announcements(self, limit: int = 5) -> List[Announcement]:
        """查询置顶公告"""
        try:
            return await self.find_by_filters(
                filters={
                    "is_pinned": True,
                    "status": "published",
                    "review_status": "approved"
                },
                limit=limit,
                order_by="publish_time DESC"
            )
        except Exception as e:
            logger.error(f"查询置顶公告失败: {e}")
            return []
    
    async def search_announcements(
        self,
        keyword: str,
        category: Optional[str] = None,
        date_range: Optional[Dict[str, datetime]] = None,
        limit: int = 50
    ) -> List[Announcement]:
        """搜索公告"""
        try:
            filters = {
                "status": "published",
                "review_status": "approved"
            }
            
            # 简化的关键词搜索（实际应该支持全文搜索）
            if keyword:
                filters["$or"] = [
                    {"title": {"$regex": keyword, "$options": "i"}},
                    {"content": {"$regex": keyword, "$options": "i"}},
                    {"summary": {"$regex": keyword, "$options": "i"}}
                ]
            
            if category:
                filters["category"] = category
            
            if date_range:
                if date_range.get("start"):
                    filters["publish_time"] = {"$gte": date_range["start"]}
                if date_range.get("end"):
                    filters.setdefault("publish_time", {})["$lte"] = date_range["end"]
            
            return await self.find_by_filters(
                filters=filters,
                limit=limit,
                order_by="publish_time DESC"
            )
            
        except Exception as e:
            logger.error(f"搜索公告失败: {e}")
            return []
    
    # === 新增方法：支持重构后的Controller ===
    
    async def mark_as_read(self, announcement_id: str, user_id: str) -> Dict[str, Any]:
        """标记公告已读"""
        try:
            read_record = {
                "read_id": f"RD{datetime.now().strftime('%Y%m%d%H%M%S')}",
                "user_id": user_id,
                "announcement_id": announcement_id,
                "read_time": datetime.now().isoformat(),
                "is_deleted": False
            }
            
            # 使用基类的HTTP客户端插入数据
            result = await self.client._request(
                "POST",
                "/insert/announcement_reads",
                json_data=read_record
            )
            
            return read_record
            
        except Exception as e:
            logger.error(f"标记已读失败: {e}")
            return {"error": f"标记已读失败: {str(e)}"}
    
    async def is_read(self, announcement_id: str, user_id: str) -> bool:
        """检查公告是否已读"""
        try:
            # 查询用户是否已读该公告
            read_result = await self.client.query_table(
                "announcement_reads",
                filters={
                    "announcement_id": announcement_id,
                    "user_id": user_id,
                    "is_deleted": False
                },
                limit=1
            )
            
            reads = read_result.get("data", {}).get("records", [])
            return len(reads) > 0
            
        except Exception as e:
            logger.error(f"检查已读状态失败: {e}")
            return False
    
    async def is_bookmarked(self, announcement_id: str, user_id: str) -> bool:
        """检查是否已收藏"""
        try:
            # 🚧 [未实现] 收藏功能
            # TODO: 实现公告收藏功能
            return False
        except Exception as e:
            logger.error(f"检查收藏状态失败: {e}")
            return False
    
    async def toggle_like(self, announcement_id: str, user_id: str) -> Dict[str, Any]:
        """切换点赞状态"""
        try:
            # 检查是否已点赞
            existing_likes = await self.client.query_table(
                "announcement_likes",
                filters={
                    "announcement_id": announcement_id,
                    "user_id": user_id,
                    "is_deleted": False
                },
                limit=1
            )
            
            likes = existing_likes.get("data", {}).get("records", [])
            
            if likes:
                # 已点赞，取消点赞
                like_id = likes[0].get("like_id")
                await self.client._request(
                    "PUT",
                    f"/update/announcement_likes/{like_id}",
                    json_data={"is_deleted": True}
                )
                return {
                    "action": "unliked",
                    "like_id": like_id,
                    "message": "取消点赞成功"
                }
            else:
                # 未点赞，添加点赞
                like_record = {
                    "like_id": f"LK{datetime.now().strftime('%Y%m%d%H%M%S')}",
                    "user_id": user_id,
                    "announcement_id": announcement_id,
                    "like_time": datetime.now().isoformat(),
                    "is_deleted": False
                }
                
                await self.client._request(
                    "POST",
                    "/insert/announcement_likes",
                    json_data=like_record
                )
                
                return {
                    "action": "liked",
                    "like_id": like_record["like_id"],
                    "message": "点赞成功"
                }
                
        except Exception as e:
            logger.error(f"切换点赞状态失败: {e}")
            return {"error": f"操作失败: {str(e)}"}
    
    async def get_read_statistics(self, announcement_id: str) -> Dict[str, Any]:
        """获取阅读统计"""
        try:
            # 查询阅读记录
            read_result = await self.client.query_table(
                "announcement_reads",
                filters={
                    "announcement_id": announcement_id,
                    "is_deleted": False
                },
                limit=100,
                order_by="read_time DESC"
            )
            
            reads = read_result.get("data", {}).get("records", [])
            
            # 查询点赞记录
            like_result = await self.client.query_table(
                "announcement_likes",
                filters={
                    "announcement_id": announcement_id,
                    "is_deleted": False
                },
                limit=100
            )
            
            likes = like_result.get("data", {}).get("records", [])
            
            return {
                "announcement_id": announcement_id,
                "read_count": len(reads),
                "like_count": len(likes),
                "recent_readers": reads[:10]  # 最近10个阅读者
            }
            
        except Exception as e:
            logger.error(f"获取阅读统计失败: {e}")
            return {
                "announcement_id": announcement_id,
                "read_count": 0,
                "like_count": 0,
                "recent_readers": [],
                "_notice": "🚧 统计数据获取失败"
            }
    
    async def get_category_list(self) -> List[Dict[str, Any]]:
        """获取公告分类列表"""
        try:
            # 🚧 [未实现] 动态分类统计
            # TODO: 从数据库中动态统计各分类的公告数量
            
            categories = [
                {"value": "education", "label": "教务通知", "count": 45},
                {"value": "student", "label": "学生事务", "count": 32},
                {"value": "academic", "label": "学术活动", "count": 28},
                {"value": "administration", "label": "行政公告", "count": 15},
                {"value": "employment", "label": "就业指导", "count": 12},
                {"value": "sports", "label": "体育活动", "count": 8},
                {"value": "other", "label": "其他", "count": 6}
            ]
            
            # 添加提醒标记
            for category in categories:
                category["_notice"] = "🚧 分类统计正在完善中"
            
            return categories
            
        except Exception as e:
            logger.error(f"获取分类列表失败: {e}")
            return []
    
    async def get_department_list(self) -> List[Dict[str, Any]]:
        """获取发布部门列表"""
        try:
            # 🚧 [未实现] 动态部门统计
            # TODO: 从数据库中动态统计各部门的公告数量
            
            departments = [
                {"value": "教务处", "label": "教务处", "count": 65},
                {"value": "学生处", "label": "学生处", "count": 42},
                {"value": "研究生院", "label": "研究生院", "count": 28},
                {"value": "人事处", "label": "人事处", "count": 18},
                {"value": "财务处", "label": "财务处", "count": 12},
                {"value": "图书馆", "label": "图书馆", "count": 8},
                {"value": "后勤处", "label": "后勤处", "count": 6}
            ]
            
            # 添加提醒标记
            for dept in departments:
                dept["_notice"] = "🚧 部门统计正在完善中"
            
            return departments
            
        except Exception as e:
            logger.error(f"获取部门列表失败: {e}")
            return []
    
    async def find_paginated(
        self, 
        filters: Dict[str, Any] = None, 
        page: int = 1, 
        size: int = 10,
        order_by: str = None
    ) -> Dict[str, Any]:
        """分页查询公告"""
        try:
            # 确保page和size是整数类型（防止HTTP查询参数传入字符串）
            page = int(page) if isinstance(page, str) else page
            size = int(size) if isinstance(size, str) else size
            
            # 添加默认过滤条件
            final_filters = {"is_deleted": False, "status": "published"}
            if filters:
                final_filters.update(filters)
            
            offset = (page - 1) * size
            
            # 调用基类的查询方法
            result = await self.client.query_table(
                table_name=self.table_name,
                filters=final_filters,
                limit=size,
                offset=offset,
                order_by=order_by
            )
            
            records = result.get("data", {}).get("records", [])
            
            # 直接使用字典数据，避免Pydantic property序列化问题
            announcements = records
            
            return {
                "announcements": announcements,
                "total": len(announcements),
                "page": page,
                "size": size,
                "pages": (len(announcements) + size - 1) // size if announcements else 0
            }
            
        except Exception as e:
            logger.error(f"分页查询公告失败: {e}")
            return {
                "announcements": [],
                "total": 0,
                "page": page,
                "size": size,
                "pages": 0
            }
    
    async def get_announcement_statistics(
        self,
        date_range: Optional[Dict[str, datetime]] = None
    ) -> Dict[str, Any]:
        """获取公告统计信息"""
        try:
            base_filters = {
                "status": "published",
                "review_status": "approved"
            }
            
            if date_range:
                if date_range.get("start"):
                    base_filters["publish_time"] = {"$gte": date_range["start"]}
                if date_range.get("end"):
                    base_filters.setdefault("publish_time", {})["$lte"] = date_range["end"]
            
            # 分类统计
            total_count = await self.count(base_filters)
            urgent_count = await self.count({**base_filters, "is_urgent": True})
            pinned_count = await self.count({**base_filters, "is_pinned": True})
            
            # 各类别统计
            category_stats = {}
            common_categories = ["education", "sports", "academic", "general", "administration"]
            
            for category in common_categories:
                count = await self.count({**base_filters, "category": category})
                if count > 0:
                    category_stats[category] = count
            
            return {
                "total_announcements": total_count,
                "urgent_announcements": urgent_count,
                "pinned_announcements": pinned_count,
                "category_statistics": category_stats
            }
            
        except Exception as e:
            logger.error(f"获取公告统计失败: {e}")
            return {
                "total_announcements": 0,
                "urgent_announcements": 0,
                "pinned_announcements": 0,
                "category_statistics": {}
            } 