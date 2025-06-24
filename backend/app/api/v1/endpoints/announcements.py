"""
公告模块 API
提供公告列表、详情、点赞等功能 - 通过HTTP请求data-service获取数据
"""
from datetime import datetime
from typing import Optional, Dict, Any
from fastapi import APIRouter, HTTPException, Query, Depends
from app.api.deps import get_current_user
# 🔄 使用HTTP客户端进行真正的HTTP请求，不导入Python模块
from app.core.http_client import http_client

router = APIRouter()

@router.get("", summary="获取公告列表")
async def get_announcements(
    category: Optional[str] = Query(None, description="公告分类"),
    priority: Optional[str] = Query(None, description="优先级"),
    is_pinned: Optional[bool] = Query(None, description="是否置顶"),
    page: int = Query(1, description="页码"),
    size: int = Query(10, description="每页数量"),
    current_user: Dict[str, Any] = Depends(get_current_user)
):
    """获取公告列表"""
    try:
        offset = (page - 1) * size
        
        filters = {
            "is_deleted": False,
            "status": "published"
        }
        
        if category:
            filters["category"] = category
        if priority:
            filters["priority"] = priority
        if is_pinned is not None:
            filters["is_pinned"] = is_pinned
        
        # 🔄 HTTP请求data-service获取公告
        result = await http_client.query_table(
            "announcements",
            filters=filters,
            limit=size,
            offset=offset,
            order_by="is_pinned DESC, publish_time DESC"
        )
        
        announcements = result.get("data", {}).get("records", [])
        
        return {
            "code": 0,
            "message": "success",
            "data": {
                "announcements": announcements,
                "total": len(announcements),
                "page": page,
                "size": size,
                "pages": (len(announcements) + size - 1) // size
            },
            "timestamp": datetime.now().isoformat(),
            "version": "v1.0"
        }
        
    except Exception as e:
        return {
            "code": 500,
            "message": f"获取公告列表失败: {str(e)}",
            "data": None,
            "timestamp": datetime.now().isoformat(),
            "version": "v1.0"
        }

@router.get("/{announcement_id}", summary="获取公告详情")
async def get_announcement_detail(
    announcement_id: str,
    current_user: Dict[str, Any] = Depends(get_current_user)
):
    """获取公告详情"""
    try:
        # 🔄 HTTP请求data-service获取公告详情
        result = await http_client.query_table(
            "announcements",
            filters={
                "announcement_id": announcement_id,
                "is_deleted": False
            },
            limit=1
        )
        
        records = result.get("data", {}).get("records", [])
        if not records:
            return {
                "code": 404,
                "message": "公告不存在",
                "data": None,
                "timestamp": datetime.now().isoformat(),
                "version": "v1.0"
            }
        
        announcement = records[0]
        
        # 增加阅读状态
        announcement["is_read"] = False  # 简化处理
        announcement["is_bookmarked"] = False  # 简化处理
        
        # 记录阅读行为（可选）
        try:
            await http_client._request(
                "POST",
                "/insert/reading_logs",
                json_data={
                    "log_id": f"RL{datetime.now().strftime('%Y%m%d%H%M%S')}",
                    "user_id": current_user["person_id"],
                    "content_type": "announcement",
                    "content_id": announcement_id,
                    "read_time": datetime.now().isoformat(),
                    "is_deleted": False
                }
            )
        except:
            pass  # 忽略记录失败
        
        return {
            "code": 0,
            "message": "success",
            "data": announcement,
            "timestamp": datetime.now().isoformat(),
            "version": "v1.0"
        }
        
    except Exception as e:
        return {
            "code": 500,
            "message": f"获取公告详情失败: {str(e)}",
            "data": None,
            "timestamp": datetime.now().isoformat(),
            "version": "v1.0"
        }

@router.post("/{announcement_id}/read", summary="标记公告已读")
async def mark_announcement_read(
    announcement_id: str,
    current_user: Dict[str, Any] = Depends(get_current_user)
):
    """标记公告已读"""
    try:
        # 记录阅读状态
        read_record = {
            "read_id": f"RD{datetime.now().strftime('%Y%m%d%H%M%S')}",
            "user_id": current_user["person_id"],
            "announcement_id": announcement_id,
            "read_time": datetime.now().isoformat(),
            "is_deleted": False
        }
        
        await http_client._request(
            "POST",
            "/insert/announcement_reads",
            json_data=read_record
        )
        
        return {
            "code": 0,
            "message": "标记已读成功",
            "data": read_record,
            "timestamp": datetime.now().isoformat(),
            "version": "v1.0"
        }
        
    except Exception as e:
        return {
            "code": 500,
            "message": f"标记已读失败: {str(e)}",
            "data": None,
            "timestamp": datetime.now().isoformat(),
            "version": "v1.0"
        }

@router.post("/{announcement_id}/like", summary="点赞公告")
async def like_announcement(
    announcement_id: str,
    current_user: Dict[str, Any] = Depends(get_current_user)
):
    """点赞公告"""
    try:
        # 🔄 HTTP请求data-service进行点赞
        like_record = {
            "like_id": f"LK{datetime.now().strftime('%Y%m%d%H%M%S')}",
            "user_id": current_user["person_id"],
            "announcement_id": announcement_id,
            "like_time": datetime.now().isoformat(),
            "is_deleted": False
        }
        
        result = await http_client._request(
            "POST",
            "/insert/announcement_likes",
            json_data=like_record
        )
        
        if result.get("status") == "success":
            return {
                "code": 0,
                "message": "点赞成功",
                "data": like_record,
                "timestamp": datetime.now().isoformat(),
                "version": "v1.0"
            }
        else:
            raise HTTPException(status_code=500, detail="点赞失败")
        
    except Exception as e:
        return {
            "code": 500,
            "message": f"点赞失败: {str(e)}",
            "data": None,
            "timestamp": datetime.now().isoformat(),
            "version": "v1.0"
        }

@router.get("/{announcement_id}/readers", summary="获取阅读统计")
async def get_announcement_readers(
    announcement_id: str,
    current_user: Dict[str, Any] = Depends(get_current_user)
):
    """获取公告阅读统计"""
    try:
        # 查询阅读记录
        read_result = await http_client.query_table(
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
        like_result = await http_client.query_table(
            "announcement_likes",
            filters={
                "announcement_id": announcement_id,
                "is_deleted": False
            },
            limit=100
        )
        
        likes = like_result.get("data", {}).get("records", [])
        
        statistics = {
            "announcement_id": announcement_id,
            "read_count": len(reads),
            "like_count": len(likes),
            "recent_readers": reads[:10]  # 最近10个阅读者
        }
        
        return {
            "code": 0,
            "message": "success",
            "data": statistics,
            "timestamp": datetime.now().isoformat(),
            "version": "v1.0"
        }
        
    except Exception as e:
        return {
            "code": 500,
            "message": f"获取阅读统计失败: {str(e)}",
            "data": None,
            "timestamp": datetime.now().isoformat(),
            "version": "v1.0"
        }

@router.get("/categories/list")
async def get_announcement_categories():
    """获取公告分类列表 - 公开访问"""
    try:
        categories = [
            {"value": "education", "label": "教务通知", "count": 45},
            {"value": "student", "label": "学生事务", "count": 32},
            {"value": "academic", "label": "学术活动", "count": 28},
            {"value": "administration", "label": "行政公告", "count": 15},
            {"value": "employment", "label": "就业指导", "count": 12},
            {"value": "sports", "label": "体育活动", "count": 8},
            {"value": "other", "label": "其他", "count": 6}
        ]
        
        return APIResponse.success({
            "categories": categories,
            "total_categories": len(categories)
        })
        
    except Exception as e:
        return APIResponse.server_error("Failed to get categories")


@router.get("/departments/list")  
async def get_announcement_departments():
    """获取发布部门列表 - 公开访问"""
    try:
        departments = [
            {"value": "教务处", "label": "教务处", "count": 65},
            {"value": "学生处", "label": "学生处", "count": 42},
            {"value": "研究生院", "label": "研究生院", "count": 28},
            {"value": "人事处", "label": "人事处", "count": 18},
            {"value": "财务处", "label": "财务处", "count": 12},
            {"value": "图书馆", "label": "图书馆", "count": 8},
            {"value": "后勤处", "label": "后勤处", "count": 6}
        ]
        
        return APIResponse.success({
            "departments": departments,
            "total_departments": len(departments)
        })
        
    except Exception as e:
        return APIResponse.server_error("Failed to get departments") 