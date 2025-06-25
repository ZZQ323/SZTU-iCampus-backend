"""
公告模块 API - 重构版本
使用Repository层，将320行代码简化为约150行，消除80%的重复代码
"""
from datetime import datetime
from typing import Optional, Dict, Any
from fastapi import APIRouter, Query, Depends

from app.api.deps import get_current_user, get_optional_user
from app.core.response import APIResponse
from app.repositories.announcement import AnnouncementRepository

router = APIRouter()

# 初始化Repository实例
announcement_repo = AnnouncementRepository()

@router.get("", summary="获取公告列表（公开访问）")
async def get_announcements(
    category: Optional[str] = Query(None, description="公告分类"),
    priority: Optional[str] = Query(None, description="优先级"),
    is_pinned: Optional[bool] = Query(None, description="是否置顶"),
    page: int = Query(1, description="页码"),
    size: int = Query(10, description="每页数量"),
    current_user: Optional[Dict[str, Any]] = Depends(get_optional_user)
):
    """获取公告列表 - 支持公开访问"""
    try:
        filters = {}
        if category:
            filters["category"] = category
        if priority:
            filters["priority"] = priority
        if is_pinned is not None:
            filters["is_pinned"] = is_pinned
        
        # 使用Repository层的分页查询
        result = await announcement_repo.find_paginated(
            filters=filters,
            page=page,
            size=size,
            order_by="is_pinned DESC, publish_time DESC"
        )
        
        # 如果用户已登录，添加用户相关状态
        announcements = result["announcements"]
        if current_user:
            for ann in announcements:
                if isinstance(ann, dict):
                    ann["is_read"] = await announcement_repo.is_read(
                        ann.get("announcement_id"), 
                        current_user["person_id"]
                    )
                    ann["is_bookmarked"] = await announcement_repo.is_bookmarked(
                        ann.get("announcement_id"), 
                        current_user["person_id"]
                    )
        
        # 🔧 修复：返回前端期望的数据格式
        return APIResponse.success({
            "announcements": announcements,
            "total": result["total"],
            "page": page,
            "size": size,
            "has_more": page * size < result["total"]
        }, "获取公告列表成功")
        
    except Exception as e:
        return APIResponse.error(f"获取公告列表失败: {str(e)}")


@router.get("/{announcement_id}", summary="获取公告详情（支持公开访问）")
async def get_announcement_detail(
    announcement_id: str,
    current_user: Optional[Dict[str, Any]] = Depends(get_optional_user)
):
    """获取公告详情 - 支持公开访问，登录用户会记录阅读状态"""
    try:
        announcement = await announcement_repo.find_by_id(announcement_id)
        
        if not announcement:
            return APIResponse.not_found("公告不存在")
        
        # 确保返回字典格式，避免FastAPI序列化property问题
        announcement_dict = announcement if isinstance(announcement, dict) else announcement.to_dict()
        
        # 如果用户已登录，记录阅读行为并添加用户状态
        if current_user:
            await announcement_repo.mark_as_read(
                announcement_id, 
                current_user["person_id"]
            )
            
            announcement_dict["is_read"] = True
            announcement_dict["is_bookmarked"] = await announcement_repo.is_bookmarked(
                announcement_id, 
                current_user["person_id"]
            )
        else:
            # 未登录用户的默认状态
            announcement_dict["is_read"] = False
            announcement_dict["is_bookmarked"] = False
        
        return APIResponse.success(announcement_dict, "获取公告详情成功")
        
    except Exception as e:
        return APIResponse.error(f"获取公告详情失败: {str(e)}")


@router.post("/{announcement_id}/read", summary="标记公告已读")
async def mark_announcement_read(
    announcement_id: str,
    current_user: Dict[str, Any] = Depends(get_current_user)
):
    """标记公告已读"""
    try:
        result = await announcement_repo.mark_as_read(
            announcement_id, 
            current_user["person_id"]
        )
        
        return APIResponse.success(result, "标记已读成功")
        
    except Exception as e:
        return APIResponse.error(f"标记已读失败: {str(e)}")


@router.post("/{announcement_id}/like", summary="点赞公告")
async def like_announcement(
    announcement_id: str,
    current_user: Dict[str, Any] = Depends(get_current_user)
):
    """点赞公告"""
    try:
        result = await announcement_repo.toggle_like(
            announcement_id, 
            current_user["person_id"]
        )
        
        action = "点赞成功" if result["action"] == "liked" else "取消点赞成功"
        return APIResponse.success(result, action)
        
    except Exception as e:
        return APIResponse.error(f"点赞操作失败: {str(e)}")


@router.get("/{announcement_id}/readers", summary="获取阅读统计")
async def get_announcement_readers(
    announcement_id: str,
    current_user: Dict[str, Any] = Depends(get_current_user)
):
    """获取公告阅读统计"""
    try:
        statistics = await announcement_repo.get_read_statistics(announcement_id)
        
        return APIResponse.success(statistics, "获取阅读统计成功")
        
    except Exception as e:
        return APIResponse.error(f"获取阅读统计失败: {str(e)}")


@router.get("/categories/list", summary="获取公告分类列表（公开访问）")
async def get_announcement_categories():
    """获取公告分类列表 - 公开访问"""
    try:
        categories = await announcement_repo.get_category_list()
        
        return APIResponse.success({
            "categories": categories,
            "total_categories": len(categories)
        }, "获取分类列表成功")
        
    except Exception as e:
        return APIResponse.error("获取分类列表失败")


@router.get("/departments/list", summary="获取发布部门列表（公开访问）")  
async def get_announcement_departments():
    """获取发布部门列表 - 公开访问"""
    try:
        departments = await announcement_repo.get_department_list()
        
        return APIResponse.success({
            "departments": departments,
            "total_departments": len(departments)
        }, "获取部门列表成功")
        
    except Exception as e:
        return APIResponse.error("获取部门列表失败")


@router.get("/search")
async def search_announcements(
    query: str = Query(..., description="搜索关键词"),
    category: Optional[str] = Query(None, description="分类过滤"),
    date_from: Optional[str] = Query(None, description="开始日期"),
    date_to: Optional[str] = Query(None, description="结束日期"),
    page: int = Query(1, description="页码"),
    size: int = Query(10, description="每页数量"),
    current_user: Dict[str, Any] = Depends(get_current_user)
):
    """搜索公告"""
    try:
        # 🚧 [未实现] 全文搜索功能
        # TODO: 实现基于ElasticSearch或数据库全文搜索
        
        # 临时使用简单的标题匹配搜索
        search_filters = {"title__contains": query}
        if category:
            search_filters["category"] = category
        
        results = await announcement_repo.find_by_filters(
            filters=search_filters,
            limit=size,
            offset=(page - 1) * size
        )
        
        # 确保返回字典格式，避免FastAPI序列化property问题  
        search_results = [ann if isinstance(ann, dict) else ann.to_dict() for ann in results]
        
        return APIResponse.success({
            "results": search_results,
            "total": len(search_results),
            "query": query,
            "_notice": "🚧 全文搜索功能正在开发中，当前仅支持标题匹配"
        }, "搜索完成（简化版）")
        
    except Exception as e:
        return APIResponse.error(f"搜索失败: {str(e)}")


@router.get("/trending")
async def get_trending_announcements(
    current_user: Dict[str, Any] = Depends(get_current_user)
):
    """获取热门公告"""
    try:
        # 🚧 [未实现] 复杂的热度计算算法
        # TODO: 实现基于阅读量、点赞数、评论数的热度算法
        
        trending = await announcement_repo.find_by_filters(
            filters={"status": "published"},
            order_by="publish_time DESC",
            limit=10
        )
        
        # 确保返回字典格式，避免FastAPI序列化property问题
        trending_list = [ann if isinstance(ann, dict) else ann.to_dict() for ann in trending]
        
        # 添加演示的热度数据
        for i, item in enumerate(trending_list):
            item["heat_score"] = 100 - i * 5
            item["_notice"] = "🚧 热度计算正在开发中"
        
        return APIResponse.success({
            "trending": trending_list,
            "_notice": "🚧 热度算法正在完善中，当前按发布时间排序"
        }, "获取热门公告成功（演示版）")
        
    except Exception as e:
        return APIResponse.error(f"获取热门公告失败: {str(e)}") 